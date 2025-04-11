import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
import torch


device = "cuda" if torch.cuda.is_available() else "cpu"

# Загружаем предобученную модель
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
model.to(device)
# Загружаем датасет
df = pd.read_csv("dataset_up2.csv")  # Укажи sep=";" если у тебя разделитель точка с запятой

# Преобразуем в список InputExample
train_data = [InputExample(texts=[row["text"], row["label"]]) for _, row in df.iterrows()]

# Даталоадер (батчи по 16 примеров)
train_dataloader = torch.utils.data.DataLoader(train_data, batch_size=16, shuffle=True)

# Функция потерь (Multiple Negative Ranking Loss)
train_loss = losses.MultipleNegativesRankingLoss(model)

# Обучение модели (1 эпоха)
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=8, warmup_steps=100)

# Сохраняем модель
model.save("fine_tuned_sbert2")
print("Модель дообучена и сохранена!")
