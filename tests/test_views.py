import pytest
from unittest.mock import patch
from datetime import datetime
import json
from src.views import accept_date


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


def test_accept_date_returns_valid_json(mock_dependencies):
    # Вызываем тестируемую функцию
    result = accept_date("2023-01-15 12:00:00")

    # Проверяем, что результат является валидным JSON
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed["greeting"] == "Добрый день"
    assert parsed["cards"] == [{"card": "1234", "balance": 1000}]
