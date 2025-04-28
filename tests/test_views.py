import pytest
from unittest.mock import patch
from datetime import datetime
import json
from src.views import accept_date



def test_accept_date_returns_valid_json(mock_dependencies):
    # Вызываем тестируемую функцию
    result = accept_date("2023-01-15 12:00:00")

    # Проверяем, что результат является валидным JSON
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed["greeting"] == "Добрый день"
    assert parsed["cards"] == [{"card": "1234", "balance": 1000}]
