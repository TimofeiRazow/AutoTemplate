from docxtpl import DocxTemplate
import pymorphy2
from dateutil import parser
import re
from jinja2 import Environment, FileSystemLoader
from docxtpl import DocxTemplate
import search_engine as se


# nomn # именительный (кто? что?)
# gent  # родительный (кого? чего?) — человека
# datv # дательный (кому? чему?) — человеку
# accs # винительный (кого? что?) — человека
# ablt  # творительный (кем? чем?) — человеком
# loct # предложный (о ком? о чем?) — человеке


MONTHS = {
    "января": "January", "февраля": "February", "марта": "March",
    "апреля": "April", "мая": "May", "июня": "June",
    "июля": "July", "августа": "August", "сентября": "September",
    "октября": "October", "ноября": "November", "декабря": "December"
}

morph = pymorphy2.MorphAnalyzer()
env = Environment(loader=FileSystemLoader("."))  # Указываем текущую папку

def normalize_date(date_str):
    """ Приведение даты к нормальному виду """
    date_str = date_str.lower().strip()

    # Удаляем слово "года", если оно есть
    date_str = re.sub(r"\bгода\b", "", date_str).strip()

    # Меняем русские месяцы на английские
    for ru, en in MONTHS.items():
        date_str = date_str.replace(ru, en)

    # Заменяем возможные разделители (, ю - и т.п.) на пробел
    date_str = re.sub(r"[юЮ,\-/.]", " ", date_str)

    try:
        return parser.parse(date_str, dayfirst=True).strftime("%d.%m.%Y")
    except ValueError:
        return "Неверный формат даты"


def inflect_phrase(phrase, case):
    """ Склонение фразы (phrase) по падежу (case)"""
    words = phrase.split()  # Разбиваем по пробелам
    inflected_words = []
    
    for word in words:
        if "-" in word:  # Если слово сложное, с дефисом
            parts = word.split("-")
            parsed = morph.parse(word)[0]
            inflected = parsed.inflect({case})
            if inflected:
                inflected_parts = inflected.word.split("-")
                new_parts = []
                for orig, new in zip(parts, inflected_parts):
                    # Если оригинальная часть начинается с заглавной, приводим новую часть к "title-case"
                    new_parts.append(new.capitalize() if orig.istitle() else new)
                inflected_word = "-".join(new_parts)
            else:
                inflected_word = word
        else:
            parsed = morph.parse(word)[0]
            inflected = parsed.inflect({case})
            inflected_word = inflected.word if inflected else word
            # Применяем преобразование только если слово не содержит дефис
            if word.istitle():
                inflected_word = inflected_word.capitalize()
        inflected_words.append(inflected_word)
    
    return " ".join(inflected_words)


def flatten_json(data):
    """ Рекурсивное извлечение ключей и значений из вложенного JSON. """
    flattened = {}
    for key, value in data.items():
        if isinstance(value, dict):
            flattened.update(flatten_json(value))
        else:
            flattened[key] = value
    return flattened


def cleanDocumentName(text):
        pattern = r"(Статья [0-9]+).*?(п\.?\s*[0-9])"
        clean_text = re.sub(pattern, r"\1 \2", text, flags=re.DOTALL)
        print("Ошибка здесь")
        clean_text = clean_text.replace("Статья", "Ст.")
        print("НЕТ")
        return clean_text


def declensionText(data):
    """ Склонение текста по падежам и добавление путей для рендера документа """
    
    
    data["user_input"]["date"] = normalize_date(data["user_input"]["date"])
    data["user_input"]["document_date"] = normalize_date(data["user_input"]["document_date"])
    data["user_input"]["receipt_date"] = normalize_date(data["user_input"]["receipt_date"])
    data["user_input"]["document_name"] = cleanDocumentName(se.search(data["user_input"]["document_name"])[0])
    print(cleanDocumentName(se.search(data["user_input"]["document_name"])[0]))
    data["settings"]["district"] = inflect_phrase(data["settings"]["district"], "gent")
    
    req = data["user_input"]["requirement"].split()
    first_word = inflect_phrase(req[0], "loct")
    other_words = " ".join(req[1:])
    data["user_input"]["requirement"] = f"{first_word} {other_words}"
    number = data["number_of_template"]
    data["installed_path"] = f"dream/postanovlenie_{number}_inst.txt"
    data["decided_path"] = f"dream/postanovlenie_{number}_dec.txt"
    return data


def renderDocument(context):
    doc = DocxTemplate(r"C:\Users\timof\OneDrive\Рабочий стол\mvp\template.docx")
    doc.jinja_env = env
    print(context)
    doc.render(context, jinja_env = env)
    doc.save("static/generic/document.docx")






