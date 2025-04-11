from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from datasets import load_dataset, Dataset
import json

# Загрузим данные из файла
with open("nlp_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dataset = Dataset.from_list(data)
dataset = dataset.train_test_split(test_size=0.1)

label_list = sorted(set(tag for example in data for tag in example["ner_tags"]))
label_to_id = {label: i for i, label in enumerate(label_list)}
id_to_label = {i: label for label, i in label_to_id.items()}

def encode_tags(tags):
    return [label_to_id[tag] for tag in tags]

dataset = dataset.map(lambda x: {
    "labels": encode_tags(x["ner_tags"])
})


from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-conversational")

def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples["tokens"], is_split_into_words=True, truncation=True, padding="max_length", max_length=128)

    labels = []
    for i, label in enumerate(examples["labels"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(label[word_idx] if label[word_idx] % 2 == 1 else label[word_idx])  # I-label continuation
            previous_word_idx = word_idx
        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs

tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True)


from transformers import AutoModelForTokenClassification, TrainingArguments, Trainer

model = AutoModelForTokenClassification.from_pretrained(
    "DeepPavlov/rubert-base-cased-conversational", 
    num_labels=len(label_list),
    id2label=id_to_label,
    label2id=label_to_id
)

training_args = TrainingArguments(
    output_dir="./ner-model",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=4,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
)

trainer.train()


trainer.save_model("./ner-custom-model")

# Затем можешь использовать:
from transformers import pipeline
ner_pipeline = pipeline("ner", model="./ner-custom-model", tokenizer=tokenizer, aggregation_strategy="simple")
print(ner_pipeline("Проверим Ивана Иванова."))
