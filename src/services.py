from pprint import pprint
import re
import pandas as pd



def find_pfone_transactions(exel_file:str)-> list[dict]:
    """
        Открываем файл и ищем конкретный формат номера
    """
    try:
        df = pd.read_excel(exel_file)
    except Exception as e:
        print(f'Ошибка при чтении {e}')
        return []

    pattern = re.compile(r'\+7[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}')

    # Функция для проверки номера в столбце "Описание"
    def contacs_psone_description(description):
        """
            Проверяем содержит ли номер телефона
        """
        if pd.isna(description):
            return  False
        return bool(pattern.search(str(description)))

    # Формируем типо отвт
    mobile_transactions = df[df['Описание'].apply(contacs_psone_description)]

    # Приводим в список словарей
    result = mobile_transactions.to_dict(orient='records')
    return result

pprint(find_pfone_transactions('../data/operations.xlsx'))

