import json
import logging
from typing import Any

from config import FILE_EX
from src.utils import (cards_masc_get, get_currency, get_path_period,
                       get_period_taim, get_stock_prices, get_taim_greeting,
                       transactions_top)

logger = logging.getLogger(__name__)

# Настройка обработчиков
file_handler = logging.FileHandler("../logs/views.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # Убедимся, что обработчик принимает все уровни

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Форматтеры
file_formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)

console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def accept_date(data_taim:str) -> list[dict[str, Any]]:
    """Функция, принимающая на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращающую JSON-ответ
    """
    # Делайем срез на определенный диапозон
    period_of_days = get_period_taim(data_taim)
    sort_period = get_path_period(FILE_EX, period_of_days)

    # 1. Приветствие
    logger.info("Вывод приветсятвия")
    greeting = get_taim_greeting()

    # 2. По каждой карте
    logger.info("Сортирую за периуд")
    user_cards = cards_masc_get(sort_period)

    # 3. Топ пяти транзакций
    logger.info("Выводим топ пяти транзакций")
    top_transactions = transactions_top(sort_period, 5)

    # 4. Курс валют
    logger.info("Вычисляю курс валют")
    currency_rates = get_currency("../data/user_settings.json")

    # 4. Курс валют
    logger.info("Проверяем стоимость акций")
    stock_prices = get_stock_prices("../data/user_settings.json")

    data = {
        "greeting": greeting,
        "cards": user_cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    logger.info("Формирую json ответ")
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data
