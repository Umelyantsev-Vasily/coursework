import logging
import os
import re

import pandas as pd

logger = logging.getLogger(__name__)

# Создаем папку logs если её нет
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

# Затем настраиваем логгер
file_handler = logging.FileHandler(
    os.path.join(log_dir, "services.log"), encoding="utf-8"
)
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


def find_pfone_transactions(exel_file: str) -> list[dict]:
    """
    Открываем файл и ищем конкретный формат номера
    """
    logger.info("Начало работы сервиса...")
    try:
        df = pd.read_excel(exel_file)
    except Exception as e:
        logger.error(f"Ошибка при чтении: {e}")
        print(f"Ошибка при чтении {e}")
        return []

    pattern = re.compile(r"\+7[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}")

    # Функция для проверки номера в столбце "Описание"
    logger.info("Проверяю номер...")

    def contacs_pfone_description(description):
        """
        Проверяем содержит ли номер телефона
        """
        if pd.isna(description):
            return False
        return bool(pattern.search(str(description)))

    # Формируем типо отвт
    logger.info("Проверка номера завершена ")
    mobile_transactions = df[df["Описание"].apply(contacs_pfone_description)]

    # Приводим в список словарей
    logger.info("Формирую список словарей...")
    result = mobile_transactions.to_dict(orient="records")
    return result
