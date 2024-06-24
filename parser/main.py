from save_to_monga import MongoDBHandler
from tg import TgParser
from dotenv import load_dotenv
import os


def main() :
    # Парсинг ТГ
    api_key = os.getenv('TG_API_KEY')
    api_hash = os.getenv('TG_API_HASH')
    tg = TgParser(api_key, api_hash)
    row_tg_data = tg.start([])
    json_to_monga = tg.parse(row_tg_data)

    # Cохраняем в Монгу
    monga_handler = MongoDBHandler()
    inserted_id = monga_handler.insert_json_with_timestamp(json_to_monga)
    print(f"Inserted document ID: {inserted_id}")




if __name__ == "__main__":
    main()