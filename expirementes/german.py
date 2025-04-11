# Установите необходимые библиотеки, если их нет
# !pip install transformers torch

from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

# Загрузка модели и токенизатора
model_name = "Grpp/rured2-ner-mdeberta-v3-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Создание NER-пайплайна
ner_pipeline = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple",  # Группировка субтокенов в полные сущности
    device=0 if torch.cuda.is_available() else -1  # Использование GPU, если доступно
)

# Пример текста для анализа (на русском языке)
text = "ПОСТАНОВЛЕНИЕ о возбуждении исполнительного производства 12.03.2022	г. Алматы Алматинская область Частный судебный исполнитель исполнительного округа Алматинского округа Алматинская область, г. Алматы, ул. Мусрепов 8, Иванов Иван Иванович рассмотрев Ст. 9 п. 11-1. исполнительная надпись; №2345785777098 от 12.03.2022 года о взыскании 150000 тенге (взыскатель ТОО Каз Трейд 432567453,  должник Разов Тимофей Дмитриевич 345698676890) поступившего 03.04.2022 года из Суд города Алматы"

# Выполнение NER
entities = ner_pipeline(text)

# Вывод результатов
for entity in entities:
    print(f"Сущность: {entity['word']}")
    print(f"  Метка: {entity['entity_group']}")
    print(f"  Позиция: {entity['start']}-{entity['end']}")
    print(f"  Уверенность: {entity['score']:.4f}\n")