# Экспертная система диагностики вредоносного ПО

Десктопное приложение на Python с Tkinter для диагностики компьютерных вирусов и вредоносного ПО на основе экспертной системы и машинного обучения.

## Основные возможности

- **Редактор базы знаний**: Позволяет экспертам добавлять и редактировать классы вредоносного ПО, диагностические признаки и их значения.
- **Система ввода данных**: Пользователь вводит значения признаков, система диагностирует класс ПО.
- **ML модель (Decision Tree)**: Обученная модель на 7500 образцов с точностью 81%.
- **Гибридная диагностика**: Использует ML модель в приоритете, fallback на правила.
- **Хранение данных**: JSON-файлы для конфигурации, PostgreSQL для логирования и расширенных возможностей.

## Установка локально

### Требования
- Python 3.10+
- pip или conda

### Шаги

1. Клонируйте репозиторий:
```bash
git clone <repo_url>
cd "Virus Diagnostic"
```

2. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Инициализируйте датасет и модель (если не сделано):
```bash
python init.py
```

5. Запустите приложение:
```bash
python app/main.py
```

## Установка через Docker

### Требования
- Docker
- Docker Compose

### Шаги

1. Перейдите в папку проекта:
```bash
cd "Virus Diagnostic"
```

2. Запустите контейнеры:
```bash
docker-compose up --build
```

3. Приложение будет доступно на `localhost:5000`

## Структура проекта

```
Virus Diagnostic/
├── app/
│   ├── main.py                  # Главное приложение с GUI
│   ├── knowledge_base.py        # Работа с базой знаний (TinyDB)
│   ├── diagnostic_engine.py     # Логика диагностики (ML + правила)
│   ├── llm_helper.py            # Интеграция с LLM (OpenAI)
│   ├── dataset_generator.py     # Генератор датасета
│   ├── ml_model.py              # ML модель (Decision Tree)
│   ├── database.py              # ORM для PostgreSQL
│   └── data/
│       ├── dataset.json         # Датасет из 7500 образцов
│       ├── model.pkl            # Обученная ML модель
│       ├── classes.json         # Классы вредоносного ПО
│       ├── features.json        # Диагностические признаки
│       ├── feature_types.json   # Типы признаков
│       ├── ranges.json          # Диапазоны значений
│       ├── class_features.json  # Признаки классов
│       └── class_values.json    # Значения признаков классов
├── Dockerfile                   # Docker-конфиг для приложения
├── docker-compose.yml           # Оркестрация контейнеров
├── init_db.sql                  # SQL скрипт инициализации БД
├── init.py                      # Скрипт инициализации
├── requirements.txt             # Python зависимости
└── README.md                    # Этот файл

```

## Машинное обучение

### Датасет
- **Размер**: 7500 образцов
- **Классы**: 11 классов вредоносного ПО + "Чистая система"
- **Признаки**: 5 диагностических признаков (CPU, Memory, Network, FileOps, RemoteManagement)
- **Распределение**: Равномерное по классам (~681 образцов на класс)

### Модель
- **Тип**: Decision Tree Classifier (scikit-learn)
- **Точность**: 81.12% на тестовой выборке
- **Параметры**:
  - max_depth: 15
  - min_samples_split: 5
  - min_samples_leaf: 2

### Важность признаков
1. Исходящий сетевой трафик (41.75%)
2. Наличие удаленного управления (22.95%)
3. Нагрузка процессора (15.08%)
4. Операции изменения файлов (14.74%)
5. Использование оперативной памяти (5.48%)

## Диагностические признаки

1. **Средняя загрузка процессора** (0-100%)
2. **Использование оперативной памяти** (0-100%)
3. **Исходящий сетевой трафик** (0-10000 Мбит/мин)
4. **Операции изменения файлов** (0-100000)
5. **Наличие устойчивого удаленного управления** (0 или 1)

## Классы вредоносного ПО

- File injector virus
- Network worm
- Trojan downloader
- Remote Access Trojan
- Banking Trojan
- Crypto-ransomware
- Wiper
- Cryptominer
- Botnet agent
- Rootkit
- Чистая система

## Использование API

### Диагностика
```python
from app.diagnostic_engine import DiagnosticEngine
from app.knowledge_base import KnowledgeBase

kb = KnowledgeBase()
engine = DiagnosticEngine(kb)

input_data = {
    'средняя загрузка процессора': 85,
    'использование оперативной памяти': 75,
    'исходящий сетевой трафик': 50,
    'операции изменения файлов': 100,
    'наличие устойчивого удаленного управления': 0
}

diagnosis = engine.diagnose(input_data)
print(f"Диагноз: {diagnosis}")
```

## Переменные окружения

Для работы с PostgreSQL через Docker:
```
DB_HOST=postgres
DB_PORT=5432
DB_USER=virusdb
DB_PASSWORD=viruspass
DB_NAME=virus_diagnostic
```

Для LLM (OpenAI):
```
OPENAI_API_KEY=your_api_key
```

## Лицензия

MIT