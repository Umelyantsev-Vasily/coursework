<h1 align="center"> 🚀 Курсовая </h1>
---

# Описание 
Приложение для анализа транзакций, которые находятся в Excel-файле. Приложение генерирует JSON-данные для веб-страниц,
формирует Excel-отчеты, а также предоставлять другие сервисы.
---
## Основные зависимости
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2.3-150458?logo=pandas&logoColor=white)
![OpenPyXL](https://img.shields.io/badge/OpenPyXL-3.1.5-2B5F75)
![Requests](https://img.shields.io/badge/Requests-2.32.3-999966?logo=python)

## Инструменты разработки
![Poetry](https://img.shields.io/badge/Poetry-2.0+-60A5FA?logo=poetry&logoColor=white)
![Flake8](https://img.shields.io/badge/Flake8-7.2.0-9999FF)
![Mypy](https://img.shields.io/badge/Mypy-1.15.0-2B6CB0)
![Black](https://img.shields.io/badge/Black-25.1.0-000000?logo=python)
![isort](https://img.shields.io/badge/isort-6.0.1-EF8336)

## Тестирование
![Pytest](https://img.shields.io/badge/Pytest-8.3.5-0A9EDC?logo=pytest)
![Coverage](https://img.shields.io/badge/Coverage-100%25-success)
![Pandas-stubs](https://img.shields.io/badge/Pandas_stubs-2.2.3.250308-130654)
## 📦 Установка
1. Убедитесь ,что у вас установлен Python 3.13 и выше.
2. Установите Poetry:
```
pip instal poetry 
```
3. Клонируйте репозиторий:
```
https://github.com/Umelyantsev-Vasily/coursework
```
4. Установите зависимости:
```
pip install -r requirements.txt
```
---
## 🏗️ Структура проекта
```
PythonProject1/
│
├── data/                  # Папка с данными
│   ├── operations.xlsx    # Файл с операциями
│   └── usersettings.json  # Пользовательские настройки
│
├── logs/                 # Папка с логами
│   ├── reports.log        # Логи модуля reports
│   ├── services.log      # Логи модуля services
│   ├── utils.log         # Логи модуля utils
│   └── views.log         # Логи модуля views
│
├── src/                  # Исходный код
│   ├── __init__.py
│   ├── main.py           # Главный скрипт
│   ├── reports.py        # Модуль отчётов
│   ├── services.py       # Модуль сервисов
│   ├── utils.py          # Вспомогательные утилиты
│   └── views.py          # Модуль представлений
│
├── tests/                # Тесты
│   ├── test_reports.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_views.py
│
├── poetry.lock          # Файл зависимостей Poetry
├── pyproject.toml       # Конфигурация проекта
└── README.md            # Документация
```
---
## 🧪 Тестирование
### Запуск тестов:
```
poetry run pytest -v --cov=src --cov-report=html
```
### Покрытие кода 
```
Name                     Stmts   Miss  Cover
--------------------------------------------
config.py                    2      0   100%
src\__init__.py              0      0   100%
src\main.py                  9      9     0%
src\reports.py              48      0   100%
src\services.py             37      0   100%
src\utils.py               192     19    90%
src\views.py                37      0   100%
tests\__init__.py            0      0   100%
tests\conftest.py           32      0   100%
tests\test_reports.py       37      0   100%
tests\test_services.py      40      0   100%
tests\test_utils.py        321      0   100%
tests\test_views.py          8      0   100%
--------------------------------------------
TOTAL                      763     28    96%

```
---
### 📊 Примеры использования
1. Фунция для приветствия
```
def get_taim_greeting():
    """Фуекция возращает: «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени."""

    detaim_user = datetime.now().hour

    if 5 <= detaim_user < 12:
        return "<< Доброе утро! >>"
    elif 12 <= detaim_user < 18:
        return "<< Добрый день! >>"
    elif 18 <= detaim_user < 22:
        return "<< Добрый вечер! >>"
    else:
        return "<< Доброй ночи >>"
```
2. Функция предаставляет данные транзакций по номеру телефона
```
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
```
---
## 📝 Логирование
```
logs/                 # Папка с логами
├── reports.log        # Логи модуля reports
├── services.log      # Логи модуля services
├── utils.log         # Логи модуля utils
└── views.log         # Логи модуля views
```
### Структура логера 
```
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
```
---
###### Документация:
- Дополнительную информацию о структуре проекта и API можно найти в [GitHab](https://github.com/Umelyantsev-Vasily/coursework)
- Дополнительную нформацию о тесте можно посмотреть: [tests](file:///C:/Users/tanec/PycharmProjects/HomWorc/htmlcov/function_index.html)
## Лицензия:

Проект распространяется под [лицензией MIT](LICENSE).
