from typing import Protocol, runtime_checkable, Any
import json
import logging
import random
from pathlib import Path

from src.task import Task, StatusEnum, PRIORITIES

logger = logging.getLogger(__name__)

@runtime_checkable
class Source(Protocol):
    """
    Протокол источника
    """

    def get_tasks(self) -> list:
        ...

class FileSource(Source):
    """
    Источник задач. Из Json файла
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def get_tasks(self) -> list:
        if not self.file_path.exists():
            return []
            
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Не получилось загрузить Json: {e}")
        return [task["payload"] for task in data]

class GeneratorSource(Source):
    """
    Источник задач. Генератор
    """

    def __init__(self, count: int, prefix: str = "gen"):
        self.count = count
        self.prefix = prefix

    def get_tasks(self) -> list:
        return [
            f"generated {self.prefix} task {i}"
            for i in range(self.count)
        ]

class ApiSource(Source):
    """
    Источник задач. Api заглушка
    """

    def __init__(self, tasks: list[dict] | None = None):
        self._tasks = tasks or []

    def get_tasks(self) -> list:
        return [item["payload"] for item in self._tasks]

    def add_task(self, payload: Any) -> None:
        self._tasks.append({"payload": payload})

def process_task(task: Task) -> None:
    """
    Обработчик задачи. Переводит статусы и печатает результат
    """
    if task.status != StatusEnum.NOT_STARTED:
        raise ValueError("Нельзя обработать задачу, которая уже начата или завершена")
    
    task.status = StatusEnum.PROCESSING
    if not task.payload:
        task.status = StatusEnum.CANCELLED
        return
        
    print(task)
    task.status = StatusEnum.COMPLETED

def collect_all(sources: list[Source]) -> list[Task]:
    """
    Собирает payload из всех источников, создает из них задачи
    и обрабатывает каждую задачу.
    
    :return: Список всех собранных задач
    """
    tasks: list[Task] = []
    
    logger.info("Запуск получения задач из источников")
    for source in sources:
        if not isinstance(source, Source):
            logger.error(f"Ошибка добавления источника {source}")
            raise TypeError("Источник не соответствует протоколу Source")
            
        source_name = type(source).__name__
        logger.info(f"Получение задач из источника: {source_name}")
        
        for payload in source.get_tasks():
            new_id = len(tasks) + 1
            rnd_priority = random.choice(PRIORITIES)
            task = Task(id=new_id, payload=payload, priority=rnd_priority)
            tasks.append(task)
            
    logger.info(f"Сбор завершен. Всего задач: {len(tasks)}. Начинаем обработку.")
    
    for task in tasks:
        process_task(task)
        
    logger.info("Обработка задач окончена")
    return tasks
