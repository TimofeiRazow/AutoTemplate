from transformers import BertTokenizer, BertForSequenceClassification
import torch
import pandas as pd
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import TrainingArguments, Trainer
import os

# Проверка файла датасета
assert os.path.exists("dataset.csv"), "Файл dataset.csv не найден!"

# Определение устройства (GPU/CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_NAME = "cointegrated/rubert-tiny2"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=41, device_map="auto"
).to(device)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

# Загрузка данных
df = pd.read_csv("dataset.csv")

# Разделение на обучающую и валидационную выборку
train_texts, val_texts, train_labels, val_labels = train_test_split(df["text"], df["label"], test_size=0.2)

train_dataset = Dataset.from_dict({"text": train_texts.tolist(), "label": train_labels.tolist()})
val_dataset = Dataset.from_dict({"text": val_texts.tolist(), "label": val_labels.tolist()})

# Токенизация
train_dataset = train_dataset.map(tokenize_function, batched=True)
val_dataset = val_dataset.map(tokenize_function, batched=True)

# Настройки тренировки
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=5,
    logging_dir="./logs",
    logging_steps=500,
    no_cuda=not torch.cuda.is_available()
)

# Создание тренера
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# Тренировка
trainer.train()

# Сохранение модели и токенизатора
model.save_pretrained("rubert_tiny_model")
tokenizer.save_pretrained("rubert_tiny_model")

# Функция классификации текста
def classify_text(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}  # Отправка на GPU
    with torch.no_grad():
        outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()
    return prediction

print(classify_text("Твой текст здесь"))
