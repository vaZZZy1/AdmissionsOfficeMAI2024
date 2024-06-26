import os
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from  ml.ml_pipeline import ml_component

def connect_to_db():
    # Загружаем настройки из .env файла
    load_dotenv('main_settings.env')
    
    # Получаем параметры соединения с базой данных из переменных окружения
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    # Устанавливаем соединение с базой данных
    return psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

def parse_json_and_save_to_db(json_data):
    # Устанавливаем соединение с базой данных
    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Парсинг JSON-данных
        data = json.loads(json_data)
        
        for applicant_id, details in data.items():
            # Пример вычисления значения для happiness_score
            happiness_score = 5 if details["tone"] in ["neutral", "нейтральный"] else 3  # Простая условная логика

            # Подготовка и выполнение SQL для вставки или обновления данных
            cursor.execute("""
                INSERT INTO mood_metrics (applicant_id, happiness_score)
                VALUES (%s, %s)
                ON CONFLICT (applicant_id) DO UPDATE SET
                    happiness_score = EXCLUDED.happiness_score
                """, (applicant_id, happiness_score))
        
        # Сохранение изменений
        conn.commit()

    except Exception as e:
        # В случае ошибки откатываем транзакцию
        if conn is not None:
            conn.rollback()
        print(f"Error: {e}")

    finally:
        # Закрываем курсор и соединение
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

# Функция для чтения конфигурации из файла .env
def read_config():
    load_dotenv('main_settings.env')  # Загружаем параметры из .env файла

# Функция для получения документов из MongoDB
def get_documents_from_mongodb(uri, db_name, collection_name, last_date):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    documents = collection.find({"date": {"$gt": last_date}})
    return list(documents)

# Функция для добавления атрибутов к документам
def add_attributes_to_documents(documents, required_attributes):
    required_attributes_list = required_attributes.split(',')
    for document in documents:
        for attr in required_attributes_list:
            document[attr] = None  # Добавляем атрибут с значением по умолчанию
    return documents

# Главная функция
def main():
    # Читаем конфигурацию
    read_config()

    # Параметры для подключения к MongoDB
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('DB_NAME')
    collection_name = os.getenv('COLLECTION_NAME')
    last_date = os.getenv('LAST_DATE')
    required_attributes = os.getenv('REQUIRED_ATTRIBUTES')

    # Получаем документы из MongoDB
    documents = get_documents_from_mongodb(mongodb_uri, db_name, collection_name, last_date)

    # Добавляем атрибуты к документам
    updated_documents = add_attributes_to_documents(documents, required_attributes)

    data_from_ml = ml_component(updated_documents)

    parse_json_and_save_to_db(data_from_ml)

if __name__ == "__main__":
    main()
