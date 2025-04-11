import os

def split_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    part1 = []
    part2 = []
    start = False
    end = False
    for line in content:
        if end:
            part2.append(line)
        if "ПОСТАНОВИЛ" in line:
            start = False
            end = True
        if start:
            part1.append(line)

        if "УСТАНОВИЛ" in line:
            start = True
    # Создание новых файлов
    base_name = os.path.splitext(file_path)[0]
    with open(f"{base_name}_inst.txt", 'w', encoding='utf-8') as file:
        file.writelines(part1)
    with open(f"{base_name}_dec.txt", 'w', encoding='utf-8') as file:
        file.writelines(part2)

# Укажи папку с файлами
folder_path = "assignments"

for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):  # Только текстовые файлы
        split_file(os.path.join(folder_path, filename))
