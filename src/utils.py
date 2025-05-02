import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

from config import FILE_JSON

logger = logging.getLogger(__name__)

# Создаем папку logs если её нет
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

# Затем настраиваем логгер
file_handler = logging.FileHandler(os.path.join(log_dir, "utils.log"), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # Убедимся, что обработчик принимает все уровни

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Форматтеры
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)

console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


load_dotenv()
# Курс валют
EXCHANGE_RATES_API_KEY = os.getenv("API_KEY")
BASE_API_URL = "https://api.apilayer.com/exchangerates_data/convert"

# Акции
MARKETSTACK_API_KEY = os.getenv("API_KEY_MarketStack")
MARKETSTACK_BASE_API_URL = "http://api.marketstack.com/v1"


def get_taim_greeting():
    """Фуекция возращает: «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени."""

    detaim_user = datetime.now().hour

    if 5 <= detaim_user < 12:
        return "<< Доброе утро! >>"
    elif 12 <= detaim_user < 18:
        return "<< Добрый день! >>"
    elif 18 <= detaim_user < 22:
        return "<< Добрый вечер! >>"
    else:
        return "<< Доброй ночи >>"


def get_period_taim(data_taim: str, data_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """
    Функция которая принимает data_taim и возращает периуд с 1 дня месяца по следующий
    """
    logger.info("Расчитываю переуд с 1 дня месяца по следующий")
    try:
        dt = datetime.strptime(data_taim, data_format)
        first_days_of_the_month = dt.replace(day=1)
        final_data_period = [
            first_days_of_the_month.strftime("%d.%m.%Y %H:%M:%S"),
            dt.strftime("%d.%m.%Y %H:%M:%S"),
        ]
        return final_data_period
    except ValueError as e:
        logger.error(f"Ошибка формата даты: {e}")
        print(f"Ошибка формата даты: {e}. Ожидаемый формат: {data_format}")
        return []
    except TypeError as e:
        logger.error(f"Ошибка типа данных: {e}")
        print(f"Ошибка типа данных: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке даты: {e}")
        print(f"Неожиданная ошибка при обработке даты: {e}")
        return []


def get_path_period(path_file: str, period_data: str) -> DataFrame:
    """Функция принимает путь к operations.xlsx файлу, периуд дат и возращает
    таблицу в заданном периуде
    """
    logger.info("Расчитываю таблицу...")
    try:
        df = pd.read_excel(path_file, sheet_name="Отчет по операциям")

        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

        start_date = datetime.strptime(period_data[0], "%d.%m.%Y %H:%M:%S")
        end_data = datetime.strptime(period_data[1], "%d.%m.%Y %H:%M:%S")

        filter_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_data)]

        sorted_df = filter_df.sort_values(by="Дата операции")

        return sorted_df

    except FileNotFoundError as e:
        logger.error(f"Ошибка:{e} Файл {path_file} не найден")
        print(f"Ошибка: Файл {path_file} не найден")
        return pd.DataFrame()
    except ValueError as e:
        logger.error(f"Ошибка значения: {e}")
        print(f"Ошибка значения: {e}")
        return pd.DataFrame()
    except KeyError as e:
        logger.error(f"Ошибка ключа: {e}")
        print(f"Ошибка ключа: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        print(f"Неожиданная ошибка: {e}")
        return pd.DataFrame()


def cards_masc_get(sort_period: DataFrame) -> list[dict]:
    """
    Функция принимает DataFrame и возвращает список карт с расходами.
    Возвращает полные номера карт (без звёздочек) и положительный кэшбэк.
    Суммирует все операции по каждой карте.
    """
    logger.info("Расчитываю список карт с расходами...")
    try:
        transactions_cards = []

        # Убедимся, что суммы - числа
        sort_period["Сумма операции"] = pd.to_numeric(sort_period["Сумма операции"], errors="coerce")
        sort_period["Сумма операции с округлением"] = pd.to_numeric(
            sort_period["Сумма операции с округлением"], errors="coerce"
        )
        sort_period["Кэшбэк"] = pd.to_numeric(sort_period["Кэшбэк"], errors="coerce")

        # Оставляем только расходные операции
        expenses = sort_period[sort_period["Сумма операции"] < 0].copy()

        # Очищаем номер карты
        expenses["last_digits"] = expenses["Номер карты"].astype(str).str.replace("*", "")

        # Группируем по картам и суммируем
        grouped = (
            expenses.groupby("last_digits").agg({"Сумма операции с округлением": "sum", "Кэшбэк": "sum"}).reset_index()
        )

        for _, row in grouped.iterrows():
            transactions_cards.append(
                {
                    "last_digits": row["last_digits"],
                    "total_spent": abs(row["Сумма операции с округлением"]),  # Берем модуль суммы
                    "cashback": abs(row["Кэшбэк"]),  # Берем модуль кэшбэка
                }
            )

    except KeyError as e:
        logger.error(f"Ошибка доступа к колонке данных: {e}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {e}")
        return []

    return transactions_cards


# def cards_masc_get(sort_period: DataFrame) -> list[dict]:
#     """
#     Функция которая принимает DataFrame  и возращает список карт с расходами
#     """
#     logger.info("Расчитываю список карт с расходами...")
#     try:
#         transactions_cards = []
#
#         card_sort = sort_period[
#             ["Номер карты", "Сумма операции", "Кэшбэк", "Сумма операции с округлением"]
#         ]
#         for index, value in card_sort.iterrows():
#             if value["Сумма операции"] < 0:
#                 last_digits = str(value["Номер карты"]).replace("*", "")
#                 total_spent = value["Сумма операции с округлением"]
#                 cashback = total_spent // 100
#
#                 row_dict = {
#                     "last_digits": last_digits,
#                     "total_spent": total_spent,
#                     "cashback": cashback,
#                 }
#                 transactions_cards.append(row_dict)
#
#     except KeyError as e:
#         logger.error(f"Ошибка доступа к колонке данных: {e}")
#         print(f"Ошибка доступа к колонке данных: {e}")
#         return []
#     except TypeError as e:
#         logger.error(f"Ошибка типа данных: {e}")
#         print(f"Ошибка типа данных: {e}")
#         return []
#     except ValueError as e:
#         logger.error(f"Ошибка значения параметра: {e}")
#         print(f"Ошибка значения параметра: {e}")
#         return []
#     except Exception as e:
#         logger.error(f"Неожиданная ошибка при обработке транзакций: {e}")
#         print(f"Неожиданная ошибка при обработке транзакций: {e}")
#         return []
#
#     return transactions_cards


def transactions_top(sort_period: DataFrame, top_get):
    """
    Функция принимает DataFrame и возращает топ транзакций по сумме платежа
    """
    logger.info("Расчитываю топ транзакции по сумме платежа")
    try:
        title_top_transaction = []
        sorted_pay = sort_period.sort_values(by="Сумма операции", ascending=False)
        top_transaction = sorted_pay.head(top_get)
        top_transaction_sorted = top_transaction[["Дата платежа", "Сумма операции", "Категория", "Описание"]]
        for index, value in top_transaction_sorted.iterrows():
            print(value)
            transaction = {
                "date": f"{value['Дата платежа']}",
                "amount": f"{value['Сумма операции']}",
                "category": f"{value['Категория']}",
                "description": f"{value['Описание']}",
            }
            title_top_transaction.append(transaction)
    except KeyError as e:
        logger.error(f"Ошибка доступа к колонке данных: {e}")
        print(f"Ошибка доступа к колонке данных: {e}")
        return []
    except TypeError as e:
        logger.error(f"Ошибка типа данных: {e}")
        print(f"Ошибка типа данных: {e}")
        return []
    except ValueError as e:
        logger.error(f"Ошибка значения параметра: {e}")
        print(f"Ошибка значения параметра: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке транзакций: {e}")
        print(f"Неожиданная ошибка при обработке транзакций: {e}")
        return []

    return title_top_transaction


def get_currency(path_file_json: str) -> list[dict]:
    """
    Функция принимает path_file_json и возращает курс валют
    """
    cerence_rates = []
    logger.info("Расчитываю курс валют...")
    try:
        logger.info("Открываю json файл")
        with open(path_file_json, "r", encoding="utf-8") as file:
            data = json.load(file)
            curences = data["user_currencies"]
            for curence in curences:
                params = {"amount": 1, "from": f"{curence}", "to": "RUB"}
                headers = {
                    "apikei": EXCHANGE_RATES_API_KEY,
                }
                response = requests.request("GET", BASE_API_URL, headers=headers, data=params)
                status_code = response.status_code
                if status_code == 200:
                    result = response.json()
                    curence_response = result["query"]["from"]
                    curence_amount = round(result["result"], 2)
                    cerence_rates.append({"currency": f"{curence_response}", "rate": f"{curence_amount}"})
    except json.JSONDecodeError:
        logger.error("Ошибка чтения JSON-файла")
        print("Ошибка чтения JSON-файла")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса к API: {e}")
        print(f"Ошибка запроса к API: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        print(f"Неожиданная ошибка: {e}")
    logger.info("Возращаю курс валют")
    return cerence_rates


def get_stock_prices(file: str) -> List[Dict[str, Any]]:
    """
    Получает данные о ценах акций из S&P500 по данным MarketStack API
    """
    logger.info("Получаю данные по акциям...")
    result = []

    try:
        # Чтение JSON файла
        logger.info("Чтение JSON файла")
        with open(FILE_JSON, "r", encoding="utf-8") as file:
            user_data = json.load(file)
            stock_symbols = user_data.get("user_stocks", [])

            # Формирование запроса к API
            logger.info("Формирование запроса к API")
            params = {
                "access_key": MARKETSTACK_API_KEY,
                "symbols": ",".join(stock_symbols),
                "limit": 1,
            }

            # Выполнение запроса
            logger.info("Выполнение запроса")
            response = requests.get(f"{MARKETSTACK_BASE_API_URL}/eod/latest", params=params, timeout=10)
            response.raise_for_status()

            api_data = response.json()

            # Обработка данных
            logger.info("Обработка данных")
            if api_data.get("data"):
                for stock in api_data["data"]:
                    result.append(
                        {
                            "stock": stock["symbol"],
                            "price": float(stock["close"]),  # Явное преобразование к float
                        }
                    )
            else:
                print("API не вернуло данных по акциям")

    except json.JSONDecodeError:
        logger.error("Ошибка: Файл не является валидным JSON")
        print("Ошибка: Файл не является валидным JSON")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        print(f"Ошибка при запросе к API: {e}")
    except KeyError as e:
        logger.error(f"Отсутствует ожидаемое поле в ответе: {e}")
        print(f"Отсутствует ожидаемое поле в ответе: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        print(f"Неожиданная ошибка: {e}")

    return result
