from typing import Dict,Any
from src.utils import get_taim_greeting, get_period_taim, get_path_period, cards_masc_get
import json



def accept_date(data_taim: str) -> Dict[str,Any]:
    """ Функция, принимающая на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и возвращающую JSON-ответ
    """

    greeting = get_taim_greeting()
    period_of_days = get_period_taim(data_taim)
    sort_period = get_path_period('../data/operations.xlsx',period_of_days)
    user_cards = cards_masc_get(sort_period)



    data = {
        'greeting':greeting
    }

    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    return json_data



