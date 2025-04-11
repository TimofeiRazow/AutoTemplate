import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
from datasets import Dataset
import numpy as np
from seqeval.metrics import classification_report
import json

# Загружаем модель и токенизатор
model_name = "cointegrated/rubert-tiny2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=33)  # 5 — пример количества классов

# Классы сущностей
label_list = ["O", "DATE", "B-TEMPLATE", "DOCUMENT_NUMBER", "EMAIL", "PHONE", "STREET", "B-CITY", "B-AREA", "I-AREA", "I-TEMPLATE",
              "B-FULLNAME", "I-FULLNAME", "B-REQUIREMENT", "I-REQUIREMENT", "B-DOCUMENT_NAME", "I-DOCUMENT_NAME", 
              "B-CLAIMANT_NAME", "I-CLAIMANT_NAME", "B-CLAIMANT_ID", "I-CLAIMANT_ID", "B-DEBTOR_NAME", "I-DEBTOR_NAME",
              "I-DEBTOR_ID", "B-DEBTOR_ID", "B-NEW_ID", "I-NEW_ID", "B-ISSUING_AUTHORITY", "I-ISSUING_AUTHORITY", 
              "B-DISTRICT", "I-DISTRICT", "I-CITY"]
label2id = {l: i for i, l in enumerate(label_list)}
id2label = {i: l for l, i in label2id.items()}

model.config.id2label = id2label
model.config.label2id = label2id

# Пример данных
with open("nlp_dataset.json", "r", encoding="utf-8") as f:
    example = json.load(f)


# Преобразуем в Dataset
dataset = Dataset.from_list(example)

# Токенизация
def tokenize_and_align_labels(example):
    tokenized_inputs = tokenizer(example["tokens"], is_split_into_words=True, truncation=True, padding="max_length", max_length=32)
    word_ids = tokenized_inputs.word_ids()
    previous_word_idx = None
    label_ids = []
    for word_idx in word_ids:
        if word_idx is None:
            label_ids.append(-100)
        elif word_idx != previous_word_idx:
            label_ids.append(label2id[example["ner_tags"][word_idx]])
        else:
            label_ids.append(label2id[example["ner_tags"][word_idx]])
        previous_word_idx = word_idx
    tokenized_inputs["labels"] = label_ids
    return tokenized_inputs

tokenized_dataset = dataset.map(tokenize_and_align_labels)

# Параметры обучения
training_args = TrainingArguments(
    output_dir="./ner_model",
    eval_strategy="epoch",
    per_device_train_batch_size=2,
    num_train_epochs=5,
    logging_steps=10,
    save_strategy="epoch"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset,
    tokenizer=tokenizer,
)

# Обучение
trainer.train()

# Предсказание
def predict(text):
    tokens = text.split()
    inputs = tokenizer(tokens, return_tensors="pt", is_split_into_words=True, truncation=True, padding="max_length", max_length=256)
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=2)
    predicted_labels = [id2label[p.item()] for p in predictions[0]]
    for token, label in zip(tokens, predicted_labels):
        print(f"{token}: {label}")

# Пример
predict("ПОСТАНОВЛЕНИЕ о возбуждении исполнительного производства 12.03.2022 г. Алматы Иванов Иван Иванович")



