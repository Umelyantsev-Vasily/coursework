from unittest.mock import patch

import pandas as pd
import pytest

from config import FILE_EX
from src.services import find_pfone_transactions

# Тестовые данные
TEST_EXCEL_DATA = [
    {"Описание": "Платеж за телефон +7(123)456-78-90", "Сумма": 100},
    {"Описание": "Оплата интернета", "Сумма": 500},
    {"Описание": "Перевод на карту +7 123 456 78 90", "Сумма": 200},
    {"Описание": None, "Сумма": 300},
    {"Описание": "Телефон 81234567890", "Сумма": 400},
]


# Мок для pd.read_excel
@pytest.fixture
def mock_excel_data():
    return pd.DataFrame(TEST_EXCEL_DATA)


def test_find_pfone_transactions_with_valid_phones(mock_excel_data):
    with patch("pandas.read_excel", return_value=mock_excel_data):
        result = find_pfone_transactions("dummy.xlsx")

        # Должны вернуться 2 транзакции с валидными номерами
        assert len(result) == 2
        assert any("+7(123)456-78-90" in item["Описание"] for item in result)
        assert any("+7 123 456 78 90" in item["Описание"] for item in result)


def test_find_pfone_transactions_with_invalid_file():
    with patch("pandas.read_excel", side_effect=Exception("File error")):
        result = find_pfone_transactions(FILE_EX)
        assert result == []


def test_find_pfone_transactions_with_no_phones(mock_excel_data):
    # Модифицируем тестовые данные, убрав номера телефонов
    no_phones_data = mock_excel_data.copy()
    no_phones_data["Описание"] = ["Оплата", "Перевод", None, "Покупка", "Счет"]

    with patch("pandas.read_excel", return_value=no_phones_data):
        result = find_pfone_transactions("no_phones.xlsx")
        assert result == []


def test_find_pfone_transactions_with_different_phone_formats(mock_excel_data):
    # Добавляем разные форматы номеров
    extra_data = mock_excel_data.copy()
    extra_data.loc[len(extra_data)] = {
        "Описание": "Телефон +7-123-456-78-90",
        "Сумма": 600,
    }
    extra_data.loc[len(extra_data)] = {"Описание": "Номер 71234567890", "Сумма": 700}

    with patch("pandas.read_excel", return_value=extra_data):
        result = find_pfone_transactions(FILE_EX)
        # Должны найти 3 валидных номера из 4 возможных (81234567890 не подходит под шаблон)
        assert len(result) == 3
        assert any("+7-123-456-78-90" in item["Описание"] for item in result)


def test_find_pfone_transactions_with_empty_description(mock_excel_data):
    # Добавляем пустые описания
    empty_data = mock_excel_data.copy()
    empty_data["Описание"] = [None, "", "   ", "  +7(123)456-78-90  ", None]

    with patch("pandas.read_excel", return_value=empty_data):
        result = find_pfone_transactions(FILE_EX)
        # Должна найти только одну транзакцию с номером
        assert len(result) == 1
        assert "+7(123)456-78-90" in result[0]["Описание"].strip()
