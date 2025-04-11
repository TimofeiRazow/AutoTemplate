ENT = ["O", "DATE", "B-TEMPLATE", "DOCUMENT_NUMBER", "EMAIL", "PHONE", "B-STREET", "B-CITY", "B-AREA", "I-AREA", "I-TEMPLATE",
    "B-FULLNAME", "I-FULLNAME", "B-REQUIREMENT", "I-REQUIREMENT", "B-DOCUMENT_NAME", "I-DOCUMENT_NAME", 
    "B-CLAIMANT_NAME", "I-CLAIMANT_NAME", "B-CLAIMANT_ID", "I-CLAIMANT_ID", "B-DEBTOR_NAME", "I-DEBTOR_NAME",
    "I-DEBTOR_ID", "B-DEBTOR_ID", "B-NEW_ID", "I-NEW_ID", "B-ISSUING_AUTHORITY", "I-ISSUING_AUTHORITY", 
    "B-DISTRICT", "I-DISTRICT", "I-CITY", "I-STREET"]

tokens=[
            "РЕШЕНИЕ", "о", "наложении", "административного", "штрафа",
            "15.05.2023", "г.", "Нур-Султан", "Акмолинская", "область", "Судья",
            "районного", "суда", "№4", "Акмолинской", "области", ",", "г.", "Нур-Султан", ",", 
            "ул.", "Абая", "24", ",", "Сидоров", "Петр", "Сергеевич", "на", "основании", "Ст.", 
            "12", "п.", "3.", "протокол", "№345678", "от", "15.05.2023", "года", "назначил", 
            "штраф", "50000", "тенге", "(", "ответчик", "ООО", "ТрансЛогистик", "123456789", "БИН", 
            ",", "нарушитель", "Иванов", "Сергей", "Викторович", "987654321098", "ИИН", ")", "поданный",
            "01.06.2023", "года", "в", "Суд", "города", "Нур-Султан"
        ]
ner_tags=[
            "B-TEMPLATE", "I-TEMPLATE", "I-TEMPLATE", "I-TEMPLATE", "I-TEMPLATE",
            "DATE", "B-CITY", "I-CITY", "B-AREA", "I-AREA",
            "O", "O", "O", "O", "B-DISTRICT", "I-DISTRICT", "B-AREA", "I-AREA", "O", "B-CITY", "I-CITY", "O", "B-STREET", "I-STREET", "I-STREET", "O",
            "B-FULLNAME", "I-FULLNAME", "I-FULLNAME", "O", "O", "B-DOCUMENT_NAME", "I-DOCUMENT_NAME", "I-DOCUMENT_NAME", "I-DOCUMENT_NAME", "I-DOCUMENT_NAME",
            "DOCUMENT_NUMBER", "O", "DATE", "O", "B-REQUIREMENT", "I-REQUIREMENT", "I-REQUIREMENT", "I-REQUIREMENT", "O", "B-CLAIMANT_NAME", "I-CLAIMANT_NAME", 
            "I-CLAIMANT_NAME", "B-CLAIMANT_ID", "I-CLAIMANT_ID", "O", "B-DEBTOR_NAME", "I-DEBTOR_NAME", "I-DEBTOR_NAME", "I-DEBTOR_NAME", "B-DEBTOR_ID", 
            "I-DEBTOR_ID", "O", "O", "DATE", "O", "B-ISSUING_AUTHORITY", "I-ISSUING_AUTHORITY", "I-ISSUING_AUTHORITY"
        ]
print(len(tokens), len(ner_tags), len(ENT))

