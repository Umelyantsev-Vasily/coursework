import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.utils import (
    get_taim_greeting,
    get_period_taim,
    get_path_period,
    cards_masc_get,
    transactions_top,
    get_currency,
    get_stock_prices,
)
import pandas as pd
from config import FILE_EX
import json
import pytest
import requests
from unittest import mock

# @patch('src.utils.datetime')
# def test_greet_func(mock_datetime):
#     mock_datetime.now.return_value.hour = 10
#     assert get_taim_greeting() == "<< Доброе утро! >>"
#
#     mock_datetime.now.return_value.hour = 15
#     assert get_taim_greeting() == "<< Добрый день! >>"
#
#     mock_datetime.now.return_value.hour = 20
#     assert get_taim_greeting() == "<< Добрый вечер! >>"
#
#     mock_datetime.now.return_value.hour = 2
#     assert get_taim_greeting() == "<< Доброй ночи >>"


def test_get_taim_greeting_morning():
    """Тестируем приветствие для утреннего времени (5-11 часов)"""
    with mock.patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = 8
        assert get_taim_greeting() == "<< Доброе утро! >>"


def test_get_taim_greeting_afternoon():
    """Тестируем приветствие для дневного времени (12-17 часов)"""
    with mock.patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = 15
        assert get_taim_greeting() == "<< Добрый день! >>"


def test_get_taim_greeting_evening():
    """Тестируем приветствие для вечернего времени (18-21 часов)"""
    with mock.patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = 20
        assert get_taim_greeting() == "<< Добрый вечер! >>"


def test_get_taim_greeting_night_late():
    """Тестируем приветствие для позднего ночного времени (22-23 часов)"""
    with mock.patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = 23
        assert get_taim_greeting() == "<< Доброй ночи >>"


def test_get_taim_greeting_night_early():
    """Тестируем приветствие для раннего ночного времени (0-4 часов)"""
    with mock.patch("src.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value.hour = 3
        assert get_taim_greeting() == "<< Доброй ночи >>"


# 2 ////////////////////////////////////////////////////////////////////////////


@patch("src.utils.datetime")
@patch("src.utils.logger")
def test_custom_date_format(mock_logger, mock_datetime):
    """Тест с нестандартным форматом даты"""
    custom_format = "%d/%m/%Y %H-%M-%S"
    test_date = "15/05/2023 14-30-00"

    mock_dt = MagicMock()
    mock_dt.replace.return_value.strftime.return_value = "01.05.2023 14:30:00"
    mock_dt.strftime.return_value = "15.05.2023 14:30:00"
    mock_datetime.strptime.return_value = mock_dt

    result = get_period_taim(test_date, custom_format)
    assert result == ["01.05.2023 14:30:00", "15.05.2023 14:30:00"]
    mock_datetime.strptime.assert_called_with(test_date, custom_format)


@patch("src.utils.datetime")
@patch("src.utils.logger")
def test_value_error_handling(mock_logger, mock_datetime):
    """Тест обработки неверного формата даты"""
    invalid_date = "invalid-date"
    mock_datetime.strptime.side_effect = ValueError("Invalid date format")

    result = get_period_taim(invalid_date)
    assert result == []
    mock_logger.error.assert_called_with("Ошибка формата даты: Invalid date format")


@patch("src.utils.datetime")
@patch("src.utils.logger")
def test_type_error_handling(mock_logger, mock_datetime):
    """Тест обработки неверного типа данных"""
    invalid_input = 12345  # Число вместо строки
    mock_datetime.strptime.side_effect = TypeError("Expected string")

    result = get_period_taim(invalid_input)
    assert result == []
    mock_logger.error.assert_called_with("Ошибка типа данных: Expected string")


@patch("src.utils.datetime")
@patch("src.utils.logger")
def test_unexpected_error_handling(mock_logger, mock_datetime):
    """Тест обработки неожиданных ошибок"""
    mock_datetime.strptime.side_effect = Exception("Unexpected error")

    result = get_period_taim("2023-05-15 14:30:00")
    assert result == []
    mock_logger.error.assert_called_with(
        "Неожиданная ошибка при обработке даты: Unexpected error"
    )


@patch("src.utils.datetime")
def test_edge_cases(mock_datetime):
    """Тест граничных случаев"""
    test_cases = [
        (
            "2023-02-28 23:59:59",
            ["01.02.2023 23:59:59", "28.02.2023 23:59:59"],
        ),  # Не високосный год
        (
            "2024-02-29 23:59:59",
            ["01.02.2024 23:59:59", "29.02.2024 23:59:59"],
        ),  # Високосный год
        (
            "2023-03-31 00:00:00",
            ["01.03.2023 00:00:00", "31.03.2023 00:00:00"],
        ),  # Месяц с 31 днем
    ]

    for input_date, expected in test_cases:
        mock_dt = MagicMock()
        mock_dt.replace.return_value.strftime.return_value = expected[0]
        mock_dt.strftime.return_value = expected[1]
        mock_datetime.strptime.return_value = mock_dt

        result = get_period_taim(input_date)
        assert result == expected


@patch("src.utils.datetime")
@patch("src.utils.logger")
def test_first_day_of_month(mock_logger, mock_datetime):
    """Тест для первого дня месяца"""
    test_date = "2023-05-01 00:00:00"

    mock_dt = MagicMock()
    mock_dt.replace.return_value.strftime.return_value = "01.05.2023 00:00:00"
    mock_dt.strftime.return_value = "01.05.2023 00:00:00"
    mock_datetime.strptime.return_value = mock_dt

    result = get_period_taim(test_date)
    assert result == ["01.05.2023 00:00:00", "01.05.2023 00:00:00"]


@patch("src.utils.datetime")
@patch("src.utils.logger")
def test_time_only_format(mock_logger, mock_datetime):
    """Тест с форматом, содержащим только время"""
    time_format = "%H:%M:%S"
    test_time = "14:30:00"

    mock_dt = MagicMock()
    mock_dt.replace.return_value.strftime.return_value = "01.01.1900 14:30:00"
    mock_dt.strftime.return_value = "01.01.1900 14:30:00"
    mock_datetime.strptime.return_value = mock_dt

    result = get_period_taim(test_time, time_format)
    assert result == ["01.01.1900 14:30:00", "01.01.1900 14:30:00"]
    mock_datetime.strptime.assert_called_with(test_time, time_format)


# 3 ///////////////////////////////////////////////////////////////////////////////////////////////////


@patch("src.utils.pd.read_excel")
def test_empty_result(mock_read_excel):
    """Тест случая, когда нет данных в указанном периоде"""
    test_data = {"Дата операции": ["01.06.2023", "15.06.2023"], "Сумма": [100, 200]}
    mock_read_excel.return_value = pd.DataFrame(test_data)

    result = get_path_period(FILE_EX, ["01.05.2023 00:00:00", "30.05.2023 23:59:59"])
    assert result.empty


@patch("src.utils.pd.read_excel")
@patch("src.utils.logger")
def test_missing_columns(mock_logger, mock_read_excel):
    """Тест обработки отсутствия нужных колонок"""
    test_data = {"Date": ["01.05.2023"], "Amount": [100]}
    mock_read_excel.return_value = pd.DataFrame(test_data)

    result = get_path_period(FILE_EX, ["01.05.2023 00:00:00", "31.05.2023 23:59:59"])

    assert result.empty
    mock_logger.error.assert_called_once()
    assert "Ошибка ключа: 'Дата операции'" in mock_logger.error.call_args[0][0]


@patch("src.utils.pd.read_excel")
@patch("src.utils.logger")
def test_custom_sheet_name(mock_logger, mock_read_excel):
    """Тест работы с кастомным именем листа"""
    mock_read_excel.return_value = pd.DataFrame(
        {"Дата операции": ["01.05.2023"], "Сумма операции": [100]}
    )

    get_path_period(FILE_EX, ["01.05.2023 00:00:00", "31.05.2023 23:59:59"])
    mock_read_excel.assert_called_with(FILE_EX, sheet_name="Отчет по операциям")


@patch("src.utils.pd.read_excel")
def test_successful_data_filtering(mock_read_excel):
    """Тест успешной фильтрации данных по периоду"""
    test_data = {
        "Дата операции": ["01.05.2023", "15.05.2023", "01.06.2023"],
        "Сумма": [100, 200, 300],
    }
    mock_read_excel.return_value = pd.DataFrame(test_data)

    result = get_path_period(FILE_EX, ["01.05.2023 00:00:00", "31.05.2023 23:59:59"])
    assert len(result) == 2
    assert list(result["Сумма"]) == [100, 200]


@patch("src.utils.pd.read_excel")
@patch("src.utils.logger")
def test_file_not_found(mock_logger, mock_read_excel):
    """Тест обработки отсутствия файла"""
    test_filename = "nonexistent_file.xlsx"
    mock_read_excel.side_effect = FileNotFoundError("File not found")

    result = get_path_period(
        test_filename, ["01.05.2023 00:00:00", "31.05.2023 23:59:59"]
    )

    assert result.empty
    # Проверяем что был вызов error с нужным началом сообщения
    mock_logger.error.assert_called_once()

    # Получаем фактический аргумент, с которым был вызван logger.error
    actual_error_message = mock_logger.error.call_args[0][0]

    # Проверяем что сообщение содержит ключевые части
    assert "Ошибка:" in actual_error_message
    assert "File not found" in actual_error_message
    assert test_filename in actual_error_message


@patch("src.utils.pd.read_excel")
@patch("src.utils.logger")
def test_empty_dataframe(mock_logger, mock_read_excel):
    """Тест обработки пустого DataFrame"""
    mock_read_excel.return_value = pd.DataFrame()

    result = get_path_period(FILE_EX, ["01.05.2023 00:00:00", "31.05.2023 23:59:59"])
    assert result.empty
    mock_logger.warning.assert_called_with("Получен пустой DataFrame")


@patch("src.utils.pd.read_excel")
@patch("src.utils.logger")
def test_invalid_date_format(mock_logger, mock_read_excel):
    """Тест обработки некорректного формата даты"""
    test_data = {
        "Дата операции": ["2023-05-01", None, "не дата"],
        "Сумма": [100, 200, 300],
    }
    mock_read_excel.return_value = pd.DataFrame(test_data)

    result = get_path_period(FILE_EX, ["01.05.2023", "31.05.2023"])

    assert result.empty
    mock_logger.error.assert_called()


@patch("src.utils.pd.read_excel")
def test_different_amount_formats(mock_read_excel):
    test_data = {
        "Дата операции": [
            "01.05.2023 00:00:00",
            "02.05.2023 12:30:00",
            "03.05.2023 23:59:59",
        ],
        "Сумма": [100, "200", "300,50"],
    }
    mock_read_excel.return_value = pd.DataFrame(test_data)

    result = get_path_period(FILE_EX, ["01.05.2023 00:00:00", "10.05.2023 23:59:59"])
    assert len(result) == 3


@patch("src.utils.pd.read_excel")
def test_non_standard_column_names(mock_read_excel):
    """Тест на нестандартные имена колонок"""
    test_data = {
        "дата операции": ["01.05.2023"],
        "СуммаОперации": [100],  # вместо "Сумма"
    }
    mock_read_excel.return_value = pd.DataFrame(test_data)

    result = get_path_period(FILE_EX, ["01.05.2023", "10.05.2023"])
    assert result.empty  # или адаптация под разные варианты названий


#  4 ///////////////////////////////////////////////////////////////////////////////////////////////////


def test_empty_dataframe():
    """Тест с пустым DataFrame"""
    df = pd.DataFrame()
    result = cards_masc_get(df)
    assert result == []


def test_no_negative_transactions():
    """Тест, когда нет операций с отрицательной суммой"""
    test_data = {
        "Номер карты": ["1234****5678"],
        "Сумма операции": [1000],  # Положительная сумма
        "Сумма операции с округлением": [1000],
    }
    df = pd.DataFrame(test_data)

    result = cards_masc_get(df)
    assert result == []


def test_missing_columns():
    """Тест с отсутствующими колонками"""
    test_data = {"Номер карты": ["1234****5678"]}
    df = pd.DataFrame(test_data)

    result = cards_masc_get(df)
    assert result == []


@patch("pandas.DataFrame.iterrows")
def test_iterrows_exception(mock_iterrows):
    """Тест обработки исключения при итерации по строкам"""
    mock_iterrows.side_effect = Exception("Iteration error")
    test_data = {"Номер карты": ["1234****5678"], "Сумма операции": [-1000]}
    df = pd.DataFrame(test_data)

    result = cards_masc_get(df)
    assert result == []


def test_zero_amount():
    """Тест обработки нулевой суммы"""
    test_data = {"Номер карты": ["1234****5678"], "Сумма операции": [0]}
    df = pd.DataFrame(test_data)

    result = cards_masc_get(df)
    assert result == []


def test_normal_case():
    """Тест нормальной работы с корректными данными"""
    test_data = {
        "Номер карты": ["1234****5678", "4321****8765"],
        "Сумма операции": [-1000, -500],
        "Кэшбэк": [10, 5],
        "Сумма операции с округлением": [-1000, -500],
    }
    df = pd.DataFrame(test_data)

    result = cards_masc_get(df)

    expected = [
        {"last_digits": "12345678", "total_spent": -1000, "cashback": 10.0},
        {"last_digits": "43218765", "total_spent": -500, "cashback": 5.0},
    ]
    assert result == expected


def test_empty_dataframe():
    """Тест с пустым DataFrame"""
    df = pd.DataFrame()
    result = cards_masc_get(df)
    assert result == []


def test_no_negative_transactions():
    """Тест, когда нет операций с отрицательной суммой"""
    test_data = {
        "Номер карты": ["1234****5678"],
        "Сумма операции": [1000],  # Положительная сумма
        "Сумма операции с округлением": [1000],
    }
    df = pd.DataFrame(test_data)

    result = cards_masc_get(df)
    assert result == []


def test_missing_columns():
    """Тест с отсутствующими колонками"""
    test_data = {"Номер карты": ["1234****5678"]}  # Нет нужных колонок
    df = pd.DataFrame(test_data)

    result = cards_masc_get(df)
    assert result == []


#  5 ////////////////////////////////////////////////////////////////////////////////////////////////////////////


def test_amount_boundaries():
    """Тест на граничные значения сумм операций"""
    test_data = {
        "Номер карты": ["1234****5678", "4321****8765", "5678****1234"],
        "Сумма операции": [-1, -99999999, 0],  # Минимальная, большая и нулевая суммы
        "Кэшбэк": [1, 999999, 0],
        "Сумма операции с округлением": [-1, -99999999, 0],
    }
    df = pd.DataFrame(test_data)
    result = cards_masc_get(df)
    assert len(result) == 2  # Должны обработаться только отрицательные суммы
    assert result[0]["total_spent"] == -1
    assert result[1]["total_spent"] == -99999999


def test_zero_cashback():
    """Тест на корректную обработку нулевого кэшбэка"""
    test_data = {
        "Номер карты": ["1234****5678"],
        "Сумма операции": [-100],
        "Кэшбэк": [0],
        "Сумма операции с округлением": [-100],
    }
    df = pd.DataFrame(test_data)
    result = cards_masc_get(df)
    assert len(result) == 1
    assert result[0]["cashback"] == 0.0  # Проверяем тип float


def test_missing_cashback_column():
    """Тест на отсутствие колонки с кэшбэком"""
    test_data = {
        "Номер карты": ["1234****5678"],
        "Сумма операции": [-1000],
        "Сумма операции с округлением": [-1000],
    }
    df = pd.DataFrame(test_data)
    result = cards_masc_get(df)
    assert len(result) == 0  # Или другая логика обработки


# Тест нормальной работы
def test_transactions_top_normal(sample_data):
    result = transactions_top(sample_data, 2)
    assert len(result) == 2
    assert result[0]["amount"] == "10000"  # Самая большая сумма должна быть первой
    assert result[1]["amount"] == "5000"


# Тест с пустым DataFrame
def test_empty_dataframe():
    empty_df = pd.DataFrame()
    result = transactions_top(empty_df, 5)
    assert result == []


# Тест с недостаточным количеством данных
def test_not_enough_data(sample_data):
    result = transactions_top(sample_data, 10)  # Запрашиваем больше, чем есть
    assert len(result) == 3  # Должны вернуть все имеющиеся


# Тест с отсутствующими колонками
def test_missing_columns():
    df = pd.DataFrame({"Wrong_column": [1, 2, 3]})
    result = transactions_top(df, 2)
    assert result == []


# Тест логирования ошибок
@patch("src.utils.logger")
def test_error_logging(mock_logger, sample_data):
    # Имитируем ошибку KeyError
    with patch("pandas.DataFrame.sort_values", side_effect=KeyError("Сумма операции")):
        result = transactions_top(sample_data, 2)
        mock_logger.error.assert_called_with(
            "Ошибка доступа к колонке данных: 'Сумма операции'"
        )
        assert result == []


# Тест вывода в консоль
@patch("builtins.print")
def test_print_output(mock_print, sample_data):
    transactions_top(sample_data, 1)
    assert mock_print.called  # Проверяем, что print был вызван


# Тест с разными типами данных
def test_different_data_types():
    df = pd.DataFrame(
        {
            "Дата платежа": [1, 2, 3],  # Числа вместо дат
            "Сумма операции": ["100", "200", "300"],  # Строки вместо чисел
            "Категория": [True, False, True],  # Булевы значения
            "Описание": [None, None, None],  # None значения
        }
    )
    result = transactions_top(df, 2)
    assert len(result) == 2
    assert result[0]["amount"] == "300"  # Сортировка строковых чисел


#  6 //////////////////////////////////////////////////////////////////////////////


# Тестовые данные
TEST_JSON_DATA = {"user_currencies": ["USD", "EUR"]}

SUCCESS_API_RESPONSE = {
    "query": {"from": "USD", "to": "RUB", "amount": 1},
    "result": 75.50,
    "info": {"rate": 75.50},
}


# Тест на ошибку чтения JSON файла
@patch("builtins.open", side_effect=json.JSONDecodeError("Error", "doc", 1))
def test_get_currency_json_error(mock_open_file):
    result = get_currency("invalid.json")
    assert result == []
    mock_open_file.assert_called()


# Тест на ошибку API запроса
@patch("builtins.open", mock_open(read_data=json.dumps(TEST_JSON_DATA)))
@patch(
    "requests.request", side_effect=requests.exceptions.RequestException("API Error")
)
def test_get_currency_api_error(mock_request):
    result = get_currency("dummy_path.json")
    assert result == []
    mock_request.assert_called()


# Тест на неожиданную ошибку
@patch("builtins.open", side_effect=Exception("Unexpected error"))
def test_get_currency_unexpected_error(mock_open_file):
    result = get_currency("dummy_path.json")
    assert result == []
    mock_open_file.assert_called()


# Тест на пустой список валют
@patch("builtins.open", mock_open(read_data=json.dumps({"user_currencies": []})))
def test_get_currency_empty_currencies():
    result = get_currency("empty_currencies.json")
    assert result == []


# Тест на корректность округления
@patch("builtins.open", mock_open(read_data=json.dumps(TEST_JSON_DATA)))
@patch("requests.request")
def test_get_currency_rounding(mock_request):
    mock_response = mock_request.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query": {"from": "USD", "to": "RUB", "amount": 1},
        "result": 75.56789,
    }

    result = get_currency("dummy_path.json")
    assert result[0]["rate"] == "75.57"


#  7 ////////////////////////////////////////////////////////////////////////////////////////////////


# Тестовые данные
TEST_JSON_DATA = {"user_stocks": ["AAPL", "MSFT", "GOOGL"]}

SUCCESS_API_RESPONSE = {
    "data": [
        {"symbol": "AAPL", "close": "175.50"},
        {"symbol": "MSFT", "close": "310.20"},
        {"symbol": "GOOGL", "close": "135.75"},
    ]
}

EMPTY_API_RESPONSE = {"data": []}


# Тест на успешное получение данных об акциях
@patch("builtins.open", mock_open(read_data=json.dumps(TEST_JSON_DATA)))
@patch("requests.get")
def test_get_stock_prices_success(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = SUCCESS_API_RESPONSE
    mock_response.raise_for_status.return_value = None

    result = get_stock_prices("dummy_path.json")

    assert len(result) == 3
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 175.50
    assert isinstance(result[0]["price"], float)
    mock_get.assert_called()


# Тест на пустой ответ от API
@patch("builtins.open", mock_open(read_data=json.dumps(TEST_JSON_DATA)))
@patch("requests.get")
def test_get_stock_prices_empty_api_response(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = EMPTY_API_RESPONSE
    mock_response.raise_for_status.return_value = None

    result = get_stock_prices("dummy_path.json")

    assert len(result) == 0
    mock_get.assert_called()


# Тест на ошибку чтения JSON файла
@patch("builtins.open", side_effect=json.JSONDecodeError("Error", "doc", 1))
def test_get_stock_prices_json_error(mock_open_file):
    result = get_stock_prices("invalid.json")
    assert result == []
    mock_open_file.assert_called()


# Тест на ошибку API запроса
@patch("builtins.open", mock_open(read_data=json.dumps(TEST_JSON_DATA)))
@patch("requests.get", side_effect=requests.exceptions.RequestException("API Error"))
def test_get_stock_prices_api_error(mock_get):
    result = get_stock_prices("dummy_path.json")
    assert result == []
    mock_get.assert_called()


# Тест на отсутствие ключа в ответе API
@patch("builtins.open", mock_open(read_data=json.dumps(TEST_JSON_DATA)))
@patch("requests.get")
def test_get_stock_prices_missing_key(mock_get):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"wrong_key": "value"}]}
    mock_response.raise_for_status.return_value = None

    result = get_stock_prices("dummy_path.json")
    assert result == []


# Тест на пустой список акций в JSON
@patch("builtins.open", mock_open(read_data=json.dumps({"user_stocks": []})))
def test_get_stock_prices_empty_stocks_list():
    result = get_stock_prices("empty_stocks.json")
    assert result == []


# Тест на неожиданную ошибку
@patch("builtins.open", side_effect=Exception("Unexpected error"))
def test_get_stock_prices_unexpected_error(mock_open_file):
    result = get_stock_prices("dummy_path.json")
    assert result == []
    mock_open_file.assert_called()
