import re
import json
from docx import Document

def extract_ner_data(text):
    """
    Функция извлекает из текста постановления необходимые данные.
    Возвращает словарь с двумя основными разделами:
    - user_input: данные исполнительного документа
    - settings: данные о судебном исполнителе и его офисе
    """
    # Изначальная структура результата
    data = {
        "user_input": {
            "date": "",
            "requirement": "",
            "document_name": "",
            "document_number": "",
            "document_date": "",
            "claimant_name": "",
            "claimant_id": "",
            "debtor_name": "",
            "debtor_id": "",
            "receipt_date": "",
            "issuing_authority": "",
            "new_id": ""
        },
        "settings": {
            "fullname": "",
            "email": "",
            "phone": "",
            "street": "",
            "city": "",
            "area": "",
            "district": ""
        }
    }

    # --- Извлечение данных для user_input ---

    # Извлекаем дату постановления (предполагается, что первая найденная дата в формате dd.mm.yyyy)
    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
    if date_match:
        data["user_input"]["date"] = date_match.group(1)

    # Извлечение названия исполнительного документа:
    # Ищем текст после слова "рассмотрев" до символа ";" (или до конца строки, если нет ";")
    doc_name_match = re.search(r'рассмотрев\s+([^;]+);', text, flags=re.IGNORECASE)
    if doc_name_match:
        # Дополняем, если встречается сокращение "Ст." вместо "Статья"
        doc_name = doc_name_match.group(1).strip()
        if doc_name.startswith("Ст."):
            doc_name = doc_name.replace("Ст.", "Статья", 1)
        data["user_input"]["document_name"] = doc_name

    # Извлекаем номер исполнительного документа (идёт после символа №)
    doc_number_match = re.search(r'№\s*([\d]+)', text)
    if doc_number_match:
        data["user_input"]["document_number"] = doc_number_match.group(1)

    # Извлекаем дату документа (ищем шаблон "от dd.mm.yyyy")
    doc_date_match = re.search(r'от\s+(\d{2}\.\d{2}\.\d{4})', text)
    if doc_date_match:
        data["user_input"]["document_date"] = doc_date_match.group(1)

    # Извлекаем требование исполнительного документа (ищем фразу "о взыскании" и до открывающейся скобки)
    requirement_match = re.search(r'о\s+взыскании\s+([^(]+)', text, flags=re.IGNORECASE)
    if requirement_match:
        data["user_input"]["requirement"] = "взыскании " + requirement_match.group(1).strip()

    # Извлекаем данные о взыскателе: имя и идентификатор
    claimant_match = re.search(r'взыскатель\s+(.+?)\s+(\d+)', text, flags=re.IGNORECASE)
    if claimant_match:
        data["user_input"]["claimant_name"] = claimant_match.group(1).strip()
        data["user_input"]["claimant_id"] = claimant_match.group(2).strip()

    # Извлекаем данные о должнике: ФИО и ИИН
    debtor_match = re.search(r'должник\s+(.+?)\s+(\d+)', text, flags=re.IGNORECASE)
    if debtor_match:
        data["user_input"]["debtor_name"] = debtor_match.group(1).strip()
        data["user_input"]["debtor_id"] = debtor_match.group(2).strip()

    # Извлекаем дату поступления исполнительного документа (ищем "поступившего dd.mm.yyyy")
    receipt_date_match = re.search(r'поступившего\s+(\d{2}\.\d{2}\.\d{4})', text)
    if receipt_date_match:
        data["user_input"]["receipt_date"] = receipt_date_match.group(1)

    # Извлекаем issuing authority (орган, выдавший документ) – текст после "из" до конца строки
    issuing_auth_match = re.search(r'из\s*(.*)$', text, flags=re.IGNORECASE)
    if issuing_auth_match:
        data["user_input"]["issuing_authority"] = issuing_auth_match.group(1).strip()

    # new_id оставить пустым, т.к. данные не присутствуют в тексте

    # --- Извлечение данных для settings ---
    # Для settings часто берут данные из строки адреса.
    # Пример: "..., г. Алматы, ул. Мусрепов 8, Иванов Иван Иванович"
    # Извлекаем город: после "г." до запятой
    city_match = re.search(r'г\.\s*([^,]+)', text)
    if city_match:
        data["settings"]["city"] = city_match.group(1).strip()

    # Извлекаем область (предполагается, что перед адресом города идет название области, либо после города)
    area_match = re.search(r'([А-Яа-я]+ская область)', text)
    if area_match:
        data["settings"]["area"] = area_match.group(1).strip()

    # Извлекаем улицу: ищем шаблон "ул. <название и номер>"
    street_match = re.search(r'ул\.\s*([^,]+)', text)
    if street_match:
        data["settings"]["street"] = "ул. " + street_match.group(1).strip()

    # Извлекаем ФИО судебного исполнителя: предполагается, что это строка после адресной части и до слова "рассмотрев"
    fullname_match = re.search(r',\s*([^,]+?)\s+рассмотрев', text)
    if fullname_match:
        data["settings"]["fullname"] = fullname_match.group(1).strip()

    # Извлекаем исполнительный округ (district)
    district_match = re.search(r'исполнительного округа\s*([^,]+)', text, flags=re.IGNORECASE)
    if district_match:
        data["settings"]["district"] = district_match.group(1).strip()

    # Поля email и phone отсутствуют в исходном тексте, их можно оставить пустыми или задать шаблон заполнения

    return data

def extract_text_advanced(file_path):
    doc = Document(file_path)
    text = []
    
    for element in doc.element.body:
        if element.tag.endswith('p'):  # Параграфы
            paragraph = [
                run.text for run in element.xpath('.//w:t')
            ]
            text.append(''.join(paragraph))
            
        elif element.tag.endswith('tbl'):  # Таблицы
            for row in element.xpath('.//w:tr'):
                row_text = []
                for cell in row.xpath('.//w:tc'):
                    cell_text = [
                        t.text for t in cell.xpath('.//w:t')
                    ]
                    row_text.append(' '.join(cell_text))
                text.append(' | '.join(row_text))
                
    return ' \n '.join(text)


if __name__ == '__main__':
    

    sample_text = extract_text_advanced("doc.docx")
    print(sample_text)
    extracted_data = extract_ner_data(sample_text)
    print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
