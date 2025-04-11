import sqlite3
from docx import Document

def read_tables_from_docx(file_path, cursor):
    doc = Document(file_path)
    for table in doc.tables:  # Перебираем все таблицы
        for row in table.rows:  # Перебираем строки
            if len(row.cells) >= 5:  # Проверяем, что есть минимум 5 ячеек
                if row.cells[0].text.strip().isdigit():
                    filename = f"assignments/postanovlenie_{row.cells[0].text.strip()}.txt"  # Укажи нужный файл
                    with open(filename, "r", encoding="utf-8") as f:
                        text = f.read()
                    cursor.execute("INSERT INTO templates (name, description, unique_elements, standart) VALUES (?, ?, ?, ?)", 
                                (row.cells[1].text.strip(),  
                                    text,
                                    row.cells[3].text.strip(),
                                    row.cells[4].text.strip()))


def get_by_name(name: str):
    cursor.execute("SELECT * FROM templates WHERE name = ?", 
               (name,))
    row = cursor.fetchone()  # Получить одну строку
    print("НАЙДЕНО\n", row)
    return row

# Подключаемся к БД
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу
cursor.execute("""
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    standart TEXT NOT NULL,
    unique_elements TEXT NOT NULL
)
""")

# Читаем данные из файла и записываем в БД
read_tables_from_docx("document.docx", cursor)
conn.commit()  # Сохраняем изменения