from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,

    Doc
)
import re

# Инициализация компонентов
segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)
dates_extractor = DatesExtractor(morph_vocab)
money_extractor = MoneyExtractor(morph_vocab)
addr_extractor = AddrExtractor(morph_vocab)

# Пример текста для анализа
text = """
ПОСТАНОВЛЕНИЕ о возбуждении исполнительного производства 12.03.2022	г. Алматы Алматинская область Частный судебный исполнитель исполнительного округа Алматинского округа Алматинская область, г. Алматы, ул. Мусрепов 8, Иванов Иван Иванович рассмотрев Ст. 9 п. 11-1. исполнительная надпись; №2345785777098 от 12.03.2022 года о взыскании 150000 тенге (взыскатель ТОО "Каз Трейд" 432567453,  должник Разов Тимофей Дмитриевич 345698676890) поступившего 03.04.2022 года из Суд города Алматы
"""
pattern = r'\bKZT\b|₸|\bтенге\b'

# Замена на символ рубля
result = re.sub(pattern, '₽', text, flags=re.IGNORECASE)
text = result
# Создание документа и применение обработчиков
doc = Doc(text)
doc.segment(segmenter)
doc.tag_morph(morph_tagger)
doc.parse_syntax(syntax_parser)
doc.tag_ner(ner_tagger)

# Лемматизация и нормализация
for token in doc.tokens:
    token.lemmatize(morph_vocab)

print("Extracted entities:")
for span in doc.spans:
    print(f"{span.text} -> {span.normal}, {span.fact} [{span.type}]")
# Извлечение именованных сущностей
print("=== Извлеченные имена ===")
for span in doc.spans:
    span.normalize(morph_vocab)
    if span.type == PER:
        span.extract_fact(names_extractor)
        print(span, '->', span.fact)

        
# Извлечение дат
print("\n=== Извлеченные даты ===")
matches = dates_extractor(text)
for match in matches:
    print(match.fact)

# Извлечение денежных сумм
print("\n=== Извлеченные денежные суммы ===")
matches = money_extractor(text)
for match in matches:
    print(match.fact)

# Извлечение адресов
print("\n=== Извлеченные адреса ===")
matches = addr_extractor(text)
for match in matches:
    print(match.fact)