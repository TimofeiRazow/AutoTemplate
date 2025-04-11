from transformers import pipeline

# Загрузка модели для QA на русском
nlp_qa = pipeline("question-answering", model="sberbank-ai/rugpt3medium_based_on_gpt2")

# Пример текста
context = "Должник Разов Тимофей Дмитриевич"
question = "Кто должник?"

# Ответ на вопрос
answer = nlp_qa(question=question, context=context)
print(answer['answer'])
