# ЛАБОРАТОРНАЯ РАБОТА №4: Асинхронный исполнитель задач

## Выполнено: Все требования реализованы успешно

### Функциональные требования
- Асинхронная очередь задач (TaskQueue с syncio.Queue)
- Контракт обработчика через Protocol (TaskHandler с @runtime_checkable)
- Контекстные менеджеры (async with для TaskExecutor)
- Централизованное логирование и обработка ошибок

### Технические требования
- Корректное использование async/await (везде где нужна асинхронность)
- Отсутствие блокирующих операций в event loop
- Расширяемая архитектура (2 обработчика: DefaultHandler, FastHandler)
- Type annotations и документация

### Тестирование
- 12 асинхронных тестов - все PASSED

## Структура проекта

src/
  - task.py          : Task, StatusEnum, PRIORITIES
  - task_queue.py    : Асинхронная очередь (AsyncIterator)
  - executor.py      : TaskExecutor, TaskHandler Protocol, обработчики
  - handler.py       : collect_and_process()
  - source.py        : Source Protocol, 3 реализации
  - main.py          : CLI интерфейс

tests/
  - test_async_executor.py : 12 асинхронных тестов

Документация:
  - LAB_REPORT.md    : Подробный отчет
  - ARCHITECTURE.md  : Описание архитектуры
  - examples.py      : 6 примеров использования

## Запуск

Тесты:
  python -m pytest tests/test_async_executor.py -v

CLI:
  python -m src.main -g 5 -a task1 -a task2
  python -m src.main -f tasks.json
  python -m src.main -g 3 -f data.json -a api_task