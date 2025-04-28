import pytest
from unittest.mock import patch
import pandas as pd
import json
from src.reports import get_dataframe
from config import FILE_EX
import logging

logging.disable(logging.CRITICAL)


@pytest.fixture(autouse=True)
def mock_logging(tmp_path):
    with patch("logging.FileHandler") as mock:
        yield


def test_spending_by_category_with_matches():
    test_data = pd.DataFrame(
        {
            "Дата операции": ["31.12.2021 16:44:00"],  # Изменено на 'Дата операции'
            "Категория": ["Перевод"],
            "Сумма": [100],
        }
    )

    with patch("pandas.read_excel", return_value=test_data):
        from src.reports import spending_by_category

        @spending_by_category(date="31.12.2021 16:44:00", category="Перевод")
        def temp_get_dataframe(filename):
            return pd.read_excel(filename)

        result = temp_get_dataframe(FILE_EX)
        data = json.loads(str(result))
        assert len(data) == 1
        assert data[0]["Сумма"] == 100


def test_spending_by_category_with_no_matches(mock_df):
    with patch("pandas.read_excel", return_value=mock_df):
        # Изменяем декоратор для другой категории
        from src.reports import spending_by_category

        @spending_by_category(date="31.12.2021 16:44:00", category="Перевод")
        def temp_get_dataframe(filename):
            return pd.read_excel(filename)

        result = temp_get_dataframe(FILE_EX)
        data = json.loads(str(result))
        assert len(data) == 0


def test_spending_by_category_with_empty_df():
    with patch("pandas.read_excel", return_value=pd.DataFrame()):
        result = get_dataframe(FILE_EX)
        data = json.loads(str(result))
        assert len(data) == 0


def test_spending_by_category_with_error_reading_file():
    with patch("pandas.read_excel", side_effect=Exception("File error")):
        with pytest.raises(Exception, match="Ошибка при чтении файла: File error"):
            get_dataframe("invalid.xlsx")
