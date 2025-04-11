import pdfplumber
import re

file_path = "temp.pdf"

with pdfplumber.open(file_path) as pdf:
    all_text = []
    for page in pdf.pages:
        lines = page.extract_text().split("\n")  # Разбиваем на строки
        all_text.extend(lines)  # Добавляем строки в общий список



# Убираем лишние пробелы и разрывы строк
text = re.sub(r"[^\S\r\n]+", " ", "\n".join(all_text)).strip()

pattern = r"Постановление.*?Место\s+печати(?:\s*\(подпись, фамилия, инициалы\))?"
matches = re.findall(pattern, text, re.S|re.I)  # Теперь .*? учитывает переносы строк!

all_text = []
for i in matches:
    all_text.append(re.sub(r"Сноска\..*?официального опубликования\)\.\s*", "", i, flags=re.S))
print(all_text[1])

if not matches:
    print("❌ Постановления не найдены. Проверь структуру текста.")
else:
    print(f"✅ Найдено {len(matches)} постановлений.")


for i, match in enumerate(all_text):
    filename = f"assignments/postanovlenie_{i+1}.txt"
    
    with open(filename, "w", encoding="utf-8", newline="\n") as f:
        f.write(match.strip()) 

    print(f"📄 Сохранено: {filename}")

