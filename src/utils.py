from datetime import datetime
import pandas as pd
from pandas import DataFrame


def get_taim_greeting():
    """ Фуекция возращает: «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
        в зависимости от текущего времени."""

    detaim_user = datetime.now().hour

    if 5 <= detaim_user < 12:
        return '<< Доброе утро! >>'
    elif 12 <= detaim_user < 18:
        return '<< Добрый день! >>'
    elif 18 <= detaim_user < 22:
        return '<< Добрый вечер! >>'
    else:
        return '<< Доброй ночи >>'


def get_period_taim(data_taim: str, data_format:str="%Y-%m-%d %H:%M:%S"):
    """

    """
    dt = datetime.strptime(data_taim, data_format )
    first_days_of_the_month = dt.replace(day=1)
    final_data_period = [first_days_of_the_month.strftime("%d.%m.%Y %H:%M:%S"),
                         dt.strftime("%d.%m.%Y %H:%M:%S")]
    return final_data_period

def get_path_period(path_file: str, period_data: str) -> DataFrame:
    """ Функция принимает путь к operations.xlsx файлу, периуд дат и возращает
     таблицу в заданном периуде"""

    df = pd.read_excel(path_file, sheet_name='Отчет по операциям')

    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)

    start_date = datetime.strptime(period_data[0], '%d.%m.%Y %H:%M:%S')
    end_data =datetime.strptime(period_data[1], '%d.%m.%Y %H:%M:%S')

    filter_df = df[
        (df['Дата операции'] >= start_date) &
        (df['Дата операции'] <= end_data)
    ]

    sorted_df = filter_df.sort_values(by= 'Дата операции')

    return  sorted_df

def cards_masc_get(sort_period: DataFrame) -> list[dict]:
    """
        Функция которая принимает DataFrame  и возращает список карт с расходами
    """
    transactions_cards = []

    card_sort = sort_period[
        [
            'Номер карты',
         'Сумма операции',
         'Кэшбэк',
         'Сумма операции с округлением'
        ]
    ]
    for index, value in card_sort.iterrows():
        print(f"Идекс:{index}, Значение: {value}")
        if value['Сумма операции'] < 0:
            last_digits = str(value['Номер карты']).replace("*","")
            total_spent = value['Сумма операции с округлением']
            cashback = value['Кэшбэк']