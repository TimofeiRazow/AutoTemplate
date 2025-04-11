import json
from deeppavlov.core.common.file import read_json
from deeppavlov import configs, train_model
import os
from deeppavlov.dataset_readers.conll2003_reader import Conll2003DatasetReader
# 1. Загружаем исходный датасет
with open("nlp_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

# 2. Преобразуем датасет в формат CoNLL с проверкой формата
import csv

# Чтение CSV файла



# 3. Настройка конфигурации
config = read_json(configs.ner.ner_rus_bert)

# Указываем пути к данным
config["dataset_reader"] = {
    "class_name": "conll2003_reader",
    "data_path": "",
    "dataset_format": "conll2003",
    "provide_pos": False,
    "docstart_mark": "",
    "file_format": "txt"
}

config["dataset_iterator"] = {
    "class_name": "data_learning_iterator",
    "seed": 42,
    "split_seed": 42,
    "split": {"train": 0.8, "valid": 0.1, "test": 0.1}
}

# 4. Обучаем модель
ner_model = train_model("config.json", download=True)

# 5. Функция для предсказания (остается без изменений)
def predict(text):
    result = ner_model([text])
    tokens, tags = result[0], result[1]
    print("Результаты NER:")
    for token, tag in zip(tokens[0], tags[0]):
        print(f"{token}: {tag}")

# Пример использования
predict("ПОСТАНОВЛЕНИЕ о возбуждении исполнительного производства 12.03.2022 г. Алматы Иванов Иван Иванович")

