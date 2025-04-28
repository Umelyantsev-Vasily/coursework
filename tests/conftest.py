import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os


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
    with (
        patch("src.views.get_period_taim") as mock_get_period,
        patch("src.views.get_path_period") as mock_get_path,
        patch("src.views.get_taim_greeting") as mock_greeting,
        patch("src.views.cards_masc_get") as mock_cards,
        patch("src.views.transactions_top") as mock_transactions,
        patch("src.views.get_currency") as mock_currency,
        patch("src.views.get_stock_prices") as mock_stocks,
        patch("src.views.logger") as mock_logger,
    ):
        yield {
            "get_period": mock_get_period,
            "get_path": mock_get_path,
            "greeting": mock_greeting,
            "cards": mock_cards,
            "transactions": mock_transactions,
            "currency": mock_currency,
            "stocks": mock_stocks,
            "logger": mock_logger,
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
