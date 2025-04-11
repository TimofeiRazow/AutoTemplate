import re
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import spacy
from spacy.lang.ru import Russian
from spacy.matcher import Matcher
from transformers import pipeline
import torch
import parser as ps
import search_engine as se
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,
    Doc
)

logger = logging.getLogger(__name__)

unused_categories_surdan = ["MONEY", "COUNTRY", "EVENT", "ORDINAL", "PROFESSION", "CRIME", "DATE", "PERSON", "ORGANIZATION","DISTRICT"]
allowed_org = ["АО", "ООО", "ТОО"]
class DocumentAnalyzer:
    def __init__(self):
        try:
            # Загрузка русской модели языка
            self.nlp = spacy.load("ru_core_news_sm")
            
            # Инициализация matcher-объекта
            self.matcher = Matcher(self.nlp.vocab)
            
            # Добавление шаблонов для распознавания сущностей
            self._add_patterns()
            
            # Инициализация NER модели
            self.ner_extractor = pipeline("token-classification", 
                                        model="surdan/LaBSE_ner_nerel", 
                                        aggregation_strategy="average")
            self.segmenter = Segmenter()
            self.morph_vocab = MorphVocab()

            emb = NewsEmbedding()
            self.morph_tagger = NewsMorphTagger(emb)
            self.syntax_parser = NewsSyntaxParser(emb)
            self.ner_tagger = NewsNERTagger(emb)

            self.names_extractor = NamesExtractor(self.morph_vocab)
            self.dates_extractor = DatesExtractor(self.morph_vocab)
            self.money_extractor = MoneyExtractor(self.morph_vocab)
            self.addr_extractor = AddrExtractor(self.morph_vocab)
        except Exception as e:
            logger.error(f"Error initializing DocumentAnalyzer: {str(e)}")
            raise

    def _add_patterns(self):
        """Добавляет уточненные шаблоны для извлечения сущностей."""
        patterns = {
            "PERSON": [
                [{"POS": "PROPN"}, {"POS": "PROPN"}, {"POS": "PROPN"}],  # ФИО из 3 слов
            ],
            "ORG": [
                [{"POS": "PROPN"}, {"POS": "PROPN", "OP": "+"}]           # Названия организаций
            ],
            "DATE": [
                [{"TEXT": {"REGEX": r"^\d{2}\.\d{2}\.\d{4}$"}}],         # 12.03.2022
                [{"TEXT": {"REGEX": r"^\d{4}-\d{2}-\d{2}$"}}],           # 2022-03-12
                [{"LIKE_NUM": True}, {"LOWER": {"IN": ["года", "год"]}}] # 12 марта 2022 года
            ],
            "IIN": [
                [{"TEXT": {"REGEX": r"^\d{12}$"}}],                      # 12 цифр подряд
                [{"TEXT": {"REGEX": r"^\d{4}\s\d{4}\s\d{4}$"}}]         # С пробелами
            ],
            "BIN": [
                [{"TEXT": {"REGEX": r"^\d{10}$"}}]                       # 10 цифр подряд
            ],
            "MONEY": [
                [{"LIKE_NUM": True}, {"LOWER": "тенге"}],
                [{"TEXT": {"REGEX": r"^\d+([.,]\d+)?₸$"}}]              # 150000₸
            ],
            "CONTRACT_NUMBER": [
                [{"TEXT": {"REGEX": r"№?\s?\d+[-/]\d+"}}]               # №1234-567
            ]
        }

        # Удаляем общие паттерны для LOC
        for label, pattern_list in patterns.items():
            self.matcher.add(label, pattern_list)

    def _preprocess_text(self, text: str) -> str:
        """
        Предварительная обработка текста для исправления артефактов OCR.
        - Удаление лишних пробелов и символов.
        - Замена часто встречающихся опечаток.
        """
        # Удаление управляющих символов и лишних пробелов
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r"\b(г|год[а]?)\b", "", text)
        
        # Пример: если OCR часто ошибается в наборах символов, можно добавить правила замены:
        # text = text.replace("браниы", "брать")
        # text = text.replace("упнараетть", "понимает")
        # Дополните данную часть своими правилами, если заметите закономерности в ошибках
        
        return text

    def analyze_structure(self, text: str) -> Dict:
        """Анализирует структуру документа (предложения и абзацы)."""
        try:
            # Предобработка текста для очистки от артефактов OCR
            text = self._preprocess_text(text)
            
            doc = self.nlp(text)
            sentences = [sent.text for sent in doc.sents]
            paragraphs = text.split('\n\n')
            
            return {
                "sentences": len(sentences),
                "paragraphs": len(paragraphs),
                "structure": {
                    "sentences": sentences,
                    "paragraphs": paragraphs
                }
            }
        except Exception as e:
            logger.error(f"Error in structure analysis: {str(e)}")
            return {
                "sentences": 0,
                "paragraphs": 0,
                "structure": {
                    "sentences": [],
                    "paragraphs": []
                }
            }

    def _concat_entities(self, ner_result):
        """
        Concatenation entities from model output on grouped entities
        """
        entities = []
        prev_entity = None
        prev_end = 0
        entities = []
        prev_entity = None
        prev_end = 0
        for i in range(len(ner_result)):
            
            if (ner_result[i]["entity_group"] == prev_entity) &\
               (ner_result[i]["start"] == prev_end):
                
                entities[i-1][2] = ner_result[i]["end"]
                prev_entity = ner_result[i]["entity_group"]
                prev_end = ner_result[i]["end"]
            else:
                entities.append([ner_result[i]["entity_group"], 
                                 ner_result[i]["start"], 
                                 ner_result[i]["end"]])
                prev_entity = ner_result[i]["entity_group"]
                prev_end = ner_result[i]["end"]
        
        return entities

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Извлекает сущности с использованием NER модели. 
        Используется 2 модели natasha и surdan/LaBSE_ner_nerel.
        Первая хорошо извлекает даты, имена, организации, локации
        """
        try:
            result = []
            doc = Doc(text)
            doc.segment(self.segmenter)
            doc.tag_morph(self.morph_tagger)
            doc.parse_syntax(self.syntax_parser)
            doc.tag_ner(self.ner_tagger)
            
            for token in doc.tokens:
                token.lemmatize(self.morph_vocab)
            matches = self.dates_extractor(text)
            for match in matches:
                date = f"{match.fact.day}.{match.fact.month}.{match.fact.year}"
                result.append({
                            "text": date,
                            "label": "DATE"
                        })
            
            for span in doc.spans:
                result.append({
                            "text": ps.inflect_phrase(span.text, "nomn") if span.type != "PER" and span.type != "ORG" else span.text,
                            "label": span.type if span.type != "PER" else "PERSON"
                        })
                
            for sequence in text.split(","):
                entities = self.ner_extractor(sequence)
                concat_ent = self._concat_entities(entities)
                
                for entity in concat_ent:
                    words = sequence[entity[1]:entity[2]]
                    if entity[0] not in unused_categories_surdan:
                        result.append({
                            "text": words,
                            "label": entity[0]
                        })
            print("Результат анализа")
            print(result)
            return result
        except Exception as e:
            logger.error(f"Error in entity extraction: {str(e)}")
            return []

    def validate_entities(self, entities: List[Dict]) -> Dict:
        """Расширенная валидация с контекстной проверкой."""
        validation_results = []
        first_law = True
        for entity in entities:
            is_valid = True
            
            # Контекстные проверки
            if entity["label"] == "PERSON":
                is_valid = bool(re.match(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$", entity["text"]))
            elif entity["label"] == "CITY":
                is_valid = not (entity["text"].isupper())
            elif entity["label"] == "LOC":
                if "Казахстан" in entity["text"] or "Республик" in entity["text"]:
                    is_valid = False
            elif entity["label"] == "LAW":
                is_valid = first_law
                if is_valid:
                    entity["text"] = se.search(entity["text"])[0]
                first_law = False
            elif entity["label"] == "ORG":
                is_valid = any([i in entity["text"] for i in allowed_org])
                if is_valid:
                    if entity["text"].count("\"") == 1:
                        entity["text"] += "\""



            if is_valid:
                validation_results.append(entity)
        
        return validation_results

    def _extract_amount(self, text: str) -> str:
        """Извлекает денежное значение с валютой из текста."""
        try:
            # Шаблон для суммы с валютой (тенге)
            amount_pattern = r'(\d+(?:[.,]\d{2})?)\s*(тенге|₸|KZT)'
            match = re.search(amount_pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
            return ""
        except Exception as e:
            logger.error(f"Error in amount extraction: {str(e)}")
            return ""

    def _validate_iin(self, iin: str) -> bool:
        """Валидация формата ИИН (должно быть 12 цифр)."""
        if len(iin) != 12:
            return False
        try:
            int(iin)
            return True
        except ValueError:
            return False

    def _validate_bin(self, bin_value: str) -> bool:
        """Валидация формата БИН (должно быть 10 цифр)."""
        if len(bin_value) != 12:
            return False
        try:
            int(bin_value)
            return True
        except ValueError:
            return False

    def _validate_date(self, date: str) -> bool:
        """Валидация формата даты."""
        try:
            datetime.strptime(date, "%d.%m.%Y")
            return True
        except ValueError:
            try:
                datetime.strptime(date, "%Y-%m-%d")
                return True
            except ValueError:
                return False
