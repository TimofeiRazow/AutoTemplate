from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NamesExtractor,
    Doc,
    MorphVocab,
    NewsNERTagger
)
from razdel import sentenize, tokenize

# Инициализация компонентов Natasha
segmenter = Segmenter()

morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
names_extractor = NamesExtractor(morph_vocab)
ner_tagger = NewsNERTagger(emb)

# Текст для обработки
text = """
Статья 228 УК РФ касается незаконного оборота наркотиков.
Федеральный закон от 21 декабря 2013 года № 273-ФЗ "О государственной гражданской службе Российской Федерации" является важным нормативным актом.
Статья 12 Гражданского кодекса РФ регулирует обязательства сторон.
"""

# Создание объекта Doc и обработка текста
doc = Doc(text)
doc.segment(segmenter)
doc.tag_morph(morph_tagger)
doc.parse_syntax(syntax_parser)
doc.tag_ner(ner_tagger)
for token in doc.tokens:
    token.lemmatize(morph_vocab)
# Вывод найденных именованных сущностей
print("Extracted entities:")
for span in doc.spans:
    print(f"{span.text} -> {span.normal} [{span.type}]")

