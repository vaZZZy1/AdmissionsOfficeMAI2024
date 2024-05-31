import dotenv
import openai
import pandas as pd
from openai import OpenAI
import os
import json
import torch
from transformers import AutoModelForSequenceClassification, BertTokenizer
from typing import Dict, Any, List, Tuple
import numpy as np
import codecs

##
model_name = 'cointegrated/rubert-base-cased-dp-paraphrase-detection'
model = AutoModelForSequenceClassification.from_pretrained(model_name).to('cpu')
tokenizer = BertTokenizer.from_pretrained(model_name)

dotenv.load_dotenv("./keys.env")

client = OpenAI(api_key=os.environ.get("API_PROXY_KEY"),
				base_url="https://api.proxyapi.ru/openai/v1")

system_prompt = codecs.open("./ml/system_prompt.txt", "r", "utf_8_sig" ).read()
# Задаётся до анализа


def request_to_GPT(data: str) -> str:
    """
    Функция для отправки запроса к API GPT-3.5

    parameters:
    data: str - Вхдные данные для анализа

    returns:
    str - Ответ от GPT-3.5
    """
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-0125",
        response_format = {"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": data
            }
        ]
    )

    return response.choices[0].message.content

def text_analysis_gpt(data: Dict[str, Any], size_batch: int = 4) -> Dict[str, Any]:
    """
    Функция для анализа множества данных

    parameters:
    data: Dict[str, Any] - Словарь ключ(str(int)) и текст сообщения сответствующее ключу
    size_batch: int - Размер батча данных для отправки запроса к API GPT

    returns:
    Dict[str, Any]: Результат анализа текстов в фрмате JSON
    """
    len_batch = size_batch
    start = 0

    output_gpt_json = {}

    while start < len(data):
        batch_data = ""

        end = start + len_batch
        if end > len(data):
            end = len(data)
        for key in list(data.keys())[start:end]:
            batch_data = batch_data + f"{key}: {data[key]}" + "\n"

        response_text = request_to_GPT(batch_data)
        output_gpt_json.update(json.loads(response_text))
        start = end

    return output_gpt_json

def compare_texts(text1:str, text2:str) -> np.ndarray:
    """
    Функция сравнения двух текстов на совпадающий смысл (парафраз)

    parameters:
    text1:str - Текст сравнения 1
    text2:str - Текст сравнения 2

    returns:
    np.ndarray: два числа от 0. до 1., второе число интерпретируется как вероятность того, что
                в текстах 1 и 2 одинаковый смысл,
                первое число интерпретируется как то, что текст 1 и текст 2 имеют разные смыслы
    """
    batch = tokenizer(text1, text2, return_tensors='pt').to(model.device)
    with torch.inference_mode():
        proba = torch.softmax(model(**batch).logits, -1).cpu().numpy()
    return proba[0]

def paraphrase_detector(df: pd.DataFrame, column: str, threshold: float = 0.5, quantity_limit: int = 100) -> Dict[str, List[Tuple[str, float]]]:
    """
    Функция для нахождения парафраз в колонке pd.DataFrame

    parameters:
    df: pd.DataFrame - DataFrame с текстовыми данными
    column: str - Имя столбца, содержащего тексты для анализа
    threshold: float = 0.5 - Пороговое значение для определение являются ли 2 текста парафразом
    quantity_limit: int = 100 - Тексты встречающиеся > quantity_limit не учитываются

    returns:
    Dict[str, List[Tuple[str, float]]] - Словарь с обнаруженными парафразами

    """

    categories = df[column].value_counts().index
    paraphrases = {category:[] for category in categories}

    unique_values = [[category, count] for category, count in zip(categories, list(df[column].value_counts()))]
    unique_values = sorted(unique_values, key = lambda w: w[1])
    for i in range(len(unique_values) - 1):
        if unique_values[i][1] > quantity_limit:
            continue
        else:
            for j in range(i + 1, len(unique_values)):
                p = compare_texts(unique_values[i][0], unique_values[j][0])[1]
                if p > threshold:
                    paraphrases[unique_values[i][0]].append((unique_values[j][0], p))

            paraphrases[unique_values[i][0]] = sorted(paraphrases[unique_values[i][0]], key = lambda w: w[1], reverse = True)

    return paraphrases

def replacing_similar_phrases(df: pd.DataFrame, columns: List[str], best_replace: bool = False) -> pd.DataFrame:
    """
    Функция заменяющая похожие фразы

    parameters:
    df: pd.DataFrame - DataFrame с текстовыми данными
    columns: List[str] - Список столбцов, где нужно заменить фразы
    best_replace: bool = False - Флаг для нахождения лучшей замены

    returns:
    pd.DataFrame - Обновленный DataFrame
    """
    for column in columns:
        similar_phrases = paraphrase_detector(df, column, threshold = 0.80)
        if best_replace:
              for category in similar_phrases.keys():
                    similar_phrases[category] = [(best_replaced(similar_phrases, category), 1.0)]

        df[column] = df[column].apply(lambda phrase: phrase if len(similar_phrases[phrase]) == 0 else similar_phrases[phrase][0][0])
    return df


def replacing_nulls(df: pd.DataFrame, columns: List[str], default_values: Any = None) -> pd.DataFrame:
    """
    Функция для замены нулевых/пустых значений

    parameters:
    df: pd.DataFrame - DataFrame с текстовыми данными
    columns: List[str] - Список столбцов, где нужно заменить нулевые/пустые значения
    default_values: Any = None - Если None, то заменяемые значения = часто встречающиеся значения,
                                  Если не None, то ожидается Dict[str, str], где ключи - это столбцы

    returns:
    pd.DataFrame - Обновленный DataFrame
    """
    if default_values is None:
        for column in columns:
            replace_null = [name for name in list(df[column].value_counts().index) if name != ""][0]
            df[column] = df[column].apply(lambda name: name if (name != "" and not (name is None)) else replace_null)

    else:
        for column in columns:
            replace_null = default_values[column]
            df[column] = df[column].apply(lambda name: name if (name != "" and not (name is None)) else replace_null)

    return df


def best_replaced(dict_replaced: Dict[str, List[Tuple[str, float]]], category: str) -> str:
    """
    Рекурсвиная функция для нахождения лучшей замены фразы

    parameters:
    dict_replaced: Dict[str, List[Tuple[str, float]]] - Словарь с заменами фраз
    category: str - Заменяемая фраза

    returns:
    str: Лучшая замена
    """
    if len(dict_replaced[category]) == 0:
        return category
    elif  len(dict_replaced[category]) == 1:
        if category == dict_replaced[category][0][0]:
            return category
        else:
            return best_replaced(dict_replaced, dict_replaced[category][0][0])
    return best_replaced(dict_replaced, dict_replaced[category][0][0])

def main_pipeline(data: Dict[str, Any]):
	output_data = text_analysis_gpt(data)

	columns = ["emotional_expression", "tone", "theme", "message_type", "communication_style"]
	default_values = {"emotional_expression": "нейтральное", "tone": "нейтральный", "theme": "нет темы", "message_type": "неопределен", "communication_style": "неформальный"}

	df_old_gpt = pd.DataFrame.from_dict(output_data, orient="index")
	df_old_gpt = replacing_nulls(df_old_gpt, columns, default_values)

	df_new_gpt = replacing_similar_phrases(df_old_gpt, columns, best_replace = True)
	return df_new_gpt
   
	
if __name__ == "__main__":
	input = open("./ml/test data/input.json")
	data = json.load(input)
   
	output_df = main_pipeline(data)
	output_df = output_df.to_json(orient = "index", index = True)
	parsed = json.loads(output_df)
	
	with open('./ml/test data/output.json', 'w') as f:
		json.dump(output_df, f)