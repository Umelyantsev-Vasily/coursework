import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os


@pytest.fixture(autouse=True)
def mock_logger():
    with patch('logging.getLogger') as mock:
        mock.return_value = MagicMock()
        yield
# Тестовые данные
TEST_DATA = [
    {"Дата операции": "01.10.2021 12:00:00", "Категория": "Супермаркеты", "Сумма": 1000},
    {"Дата операции": "15.11.2021 14:30:00", "Категория": "Супермаркеты", "Сумма": 1500},
    {"Дата операции": "31.12.2021 10:00:00", "Категория": "Рестораны", "Сумма": 2000},
    {"Дата операции": "01.01.2022 18:45:00", "Категория": "Супермаркеты", "Сумма": 1200},
]

@pytest.fixture
def mock_df():
    return pd.DataFrame(TEST_DATA)


@pytest.fixture(autouse=True)
def create_log_dir():
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)