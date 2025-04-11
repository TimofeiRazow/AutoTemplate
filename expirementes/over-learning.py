from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import Dataset
from sklearn.model_selection import train_test_split

import pandas as pd

# Путь к сохраненной модели
model_checkpoint = "./rubert_tiny_model"  # Замени на свой путь
model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint)
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

df = pd.read_csv("dataset.csv")
# Разделение данных
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["text"].tolist(), df["label"].tolist(), test_size=0.2
)

# Создание датасетов
train_dataset = Dataset.from_dict({"text": train_texts, "label": train_labels})
val_dataset = Dataset.from_dict({"text": val_texts, "label": val_labels})

# Токенизация данных
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length")

train_dataset = train_dataset.map(tokenize_function, batched=True)
val_dataset = val_dataset.map(tokenize_function, batched=True)

# Параметры обучения
training_args = TrainingArguments(
    output_dir="./checkpoints",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,  # Количество дополнительных эпох
    learning_rate=5e-6,  # Уменьшаем LR
    save_strategy="epoch",
    evaluation_strategy="epoch"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# Запуск обучения (без чекпоинта, просто с загруженной моделью)
trainer.train()
