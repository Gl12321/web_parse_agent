# Web Parse Agent

LLM-агент для извлечения структурированных данных с сайтов 

## Что делает

- Обходит сайт, начиная с заданного URL
- Использует LLM для навигации (выбор релевантных страниц) и извлечения данных
- Поддерживает strict-режим (Pydantic схемы) и flexible-режим (свободное извлечение)
- Сохраняет результаты в PostgreSQL

## Архитектура

- **FastAPI** — API
- **LangGraph** — граф обхода:
  - navigator — выбор следующей страницы
  - crawler — загрузка страницы
  - extractor — извлечение данных
  - aggregator — слияние результатов
- **SQLAlchemy + PostgreSQL** — хранение результатов
- **Docker Compose** — развёртывание

## API
- POST /api/parse          Запустить парсинг
- GET  /api/result             Получить сохранённые данные


## Требования

- API ключ 

## Структура

```
src/
  agent/nodes/           # Узлы графа
  agent/graph.py         # LangGraph workflow
  application/           # Orchestrator, сервисы
  infrastructure/        # БД, сrawler, LLM
  interfaces/api/        # FastAPI routes
  extractors/            # Flexible/strict extractors
  extractors/schemas/    # Pydantic модели (ContactInfo, OrganizationInfo, LegalInfo)
```
