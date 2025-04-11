import torch
from sentence_transformers import SentenceTransformer

# Загружаем обученную модель из папки
model = SentenceTransformer("fine_tuned_sbert")

# Сохраняем всю модель в один файл
torch.save(model, "fine_tuned_sbert.pth")

print("Модель успешно сохранена в одном файле!")

import torch

# Загружаем модель из файла
model = torch.load("fine_tuned_sbert.pth")
model.eval()  # Перевод в режим инференса

print("Модель успешно загружена!")
