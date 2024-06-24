from pymongo import MongoClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

class MongoDBHandler:
    def init(self):
        """
        Инициализация MongoDBHandler, загрузка параметров из файла .env и подключение к MongoDB.
        """
        # Загружаем настройки из .env файла
        load_dotenv('tg_settings.env')
        
        self.mongo_uri = os.getenv('MONGO_URI')
        self.database_name = os.getenv('DATABASE_NAME')
        self.collection_name = os.getenv('COLLECTION_NAME')
        
        # Соединение с MongoDB
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]

    def insert_json_with_timestamp(self, json_data):
        """
        Метод для добавления json-документа в MongoDB с полем updated_at
        :param json_data: Документ в формате JSON (словарь Python)
        :return: Идентификатор вставленного документа
        """
        # Добавляем поле updated_at с текущим временем в UTC
        json_data['updated_at'] = datetime.now(timezone.utc)
        
        # Вставка документа в коллекцию
        result = self.collection.insert_one(json_data)
        
        # Возвращаем идентификатор вставленного документа
        return result.inserted_id