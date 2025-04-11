import torch
print(torch.__version__)  # Должно быть что-то вроде 2.2.0+cu121
print(torch.cuda.is_available())  # Должно быть True
print(torch.cuda.device_count())  # Должно быть 1 (если одна видеокарта)
print(torch.cuda.get_device_name(0))  # Название твоей видеокарты
