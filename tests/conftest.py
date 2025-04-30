import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def mock_logger():
    with patch("logging.getLogger") as mock:
        mock.return_value = MagicMock()
        yield


# Тестовые данные
TEST_DATA = [
    {
        "Дата операции": "01.10.2021 12:00:00",
        "Категория": "Супермаркеты",
        "Сумма": 1000,
    },
    {
        "Дата операции": "15.11.2021 14:30:00",
        "Категория": "Супермаркеты",
        "Сумма": 1500,
    },
    {"Дата операции": "31.12.2021 10:00:00", "Категория": "Рестораны", "Сумма": 2000},
    {
        "Дата операции": "01.01.2022 18:45:00",
        "Категория": "Супермаркеты",
        "Сумма": 1200,
    },
]


@pytest.fixture
def mock_df():
    return pd.DataFrame(TEST_DATA)


@pytest.fixture(autouse=True)
def create_log_dir():
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)


@pytest.fixture
def mock_dependencies():
    # Создаем моки для всех зависимостей функции accept_date
    with (
        patch("src.views.get_period_taim") as mock_get_period,
        patch("src.views.get_path_period") as mock_get_path,
        patch("src.views.get_taim_greeting") as mock_greeting,
        patch("src.views.cards_masc_get") as mock_cards,
        patch("src.views.transactions_top") as mock_transactions,
        patch("src.views.get_currency") as mock_currency,
        patch("src.views.get_stock_prices") as mock_stocks,
        patch("src.views.logger"),
    ):
        # Настраиваем возвращаемые значения моков (реальные значения, а не MagicMock)
        mock_get_period.return_value = (datetime(2023, 1, 1), datetime(2023, 1, 31))
        mock_get_path.return_value = "mock_path"
        mock_greeting.return_value = "Добрый день"
        mock_cards.return_value = [{"card": "1234", "balance": 1000}]
        mock_transactions.return_value = [{"amount": 100, "date": "2023-01-01"}]
        mock_currency.return_value = {"USD": 75.5}
        mock_stocks.return_value = {"AAPL": 150.0}

        yield {
            "get_period": mock_get_period,
            "get_path": mock_get_path,
            "greeting": mock_greeting,
            "cards": mock_cards,
            "transactions": mock_transactions,
            "currency": mock_currency,
            "stocks": mock_stocks,
        }


# Фикстура для тестовых данных
@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "Дата платежа": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Сумма операции": [5000, 10000, 3000],
            "Категория": ["Еда", "Техника", "Одежда"],
            "Описание": ["Ресторан", "Ноутбук", "Куртка"],
        }
    )


# @pytest.fixture(autouse=True)
# def mock_logging(tmp_path):
#     with patch("logging.FileHandler") as mock:
#         yield
