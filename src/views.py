from typing import Dict,Any
from src.utils import (get_taim_greeting,
                       get_period_taim, get_path_period,
                       cards_masc_get, transactions_top,
                       get_currency,
                       get_stocks)
import json



def accept_date(data_taim: str) -> Dict[str,Any]:
    """ Функция, принимающая на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращающую JSON-ответ
    """
    # Делайем срез на определенный диапозон
    period_of_days = get_period_taim(data_taim)
    sort_period = get_path_period('../data/operations.xlsx', period_of_days)

    # 1. Приветствие
    greeting = get_taim_greeting()

    # 2. По каждой карте
    user_cards = cards_masc_get(sort_period)

    # 3. Топ пяти транзакций
    top_transactions = transactions_top(sort_period, 5)

    # 4. Курс валют
    currency_rates =  get_currency('../data/user_settings.json')

    # 4. Курс валют
    stock_prices = get_stocks('../data/user_settings.json')

    data = {
        'greeting': greeting,
        'cards': user_cards,
        'top_transactions': top_transactions,
        'currency_rates': stock_prices,
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data



