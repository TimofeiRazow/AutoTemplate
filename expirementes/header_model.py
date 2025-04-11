from datasets import Dataset
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer

# Загрузка CSV
df = pd.read_csv("dataset.csv")
dataset = Dataset.from_pandas(df)

# Разделение на train/test
dataset = dataset.train_test_split(test_size=0.1)
train_data = dataset["train"]
test_data = dataset["test"]

# Загрузка модели и токенизатора ruGPT-3 Small
model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Установка паддинга
tokenizer.pad_token = tokenizer.eos_token

# Токенизация
def tokenize_function(examples):
    input_texts = [
        f"Шаблон: {t}. Запрос: {q}. Ответ: {r}" 
        for t, q, r in zip(examples["template"], examples["query"], examples["response"])
    ]
    return tokenizer(input_texts, truncation=True, padding="max_length", max_length=128)

tokenized_train = train_data.map(tokenize_function, batched=True)
tokenized_test = test_data.map(tokenize_function, batched=True)\

# Параметры обучения
training_args = TrainingArguments(
    output_dir="./rugpt3_results",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    logging_dir="./logs",
    save_steps=500,
    evaluation_strategy="steps",
    eval_steps=500,
)

# Тренер
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
)

# Запуск обучения
trainer.train()

def generate_response(template: str, query: str) -> str:
    input_text = f"Шаблон: {template}. Запрос: {query}. Ответ:"
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")  # Для GPU
    
    outputs = model.generate(
        inputs.input_ids,
        max_length=128,
        temperature=0.7,
        num_return_sequences=1,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Пример использования
print(generate_response("Поздравление", "Для коллеги женского пола"))


# Сохранение
model.save_pretrained("./my_rugpt3")
tokenizer.save_pretrained("./my_rugpt3")

# Загрузка
model = AutoModelForCausalLM.from_pretrained("./my_rugpt3")
tokenizer = AutoTokenizer.from_pretrained("./my_rugpt3")