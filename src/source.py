from typing import Protocol, runtime_checkable, Any
import json
from loguru import logger
from pathlib import Path

from src.task import Task


@runtime_checkable
class TaskSource(Protocol):
    """
    Контракт для источника задач.
    В каждом источнике реализован метод get_tasks().
    """
    def get_tasks(self) -> list[Task]:
        ...


class FileTaskSource:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
    
    def get_tasks(self) -> list[Task]:
        if not self.file_path.exists():
            return []
        
        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        return [Task(id=item["id"], payload=item["payload"]) for item in data]


class GeneratorTaskSource:
    def __init__(self, count: int, prefix: str = "gen"):
        self.count = count
        self.prefix = prefix
    
    def get_tasks(self) -> list[Task]:
        return [
            Task(id=f"{self.prefix}_{i}", payload=f"Generated task {i}")
            for i in range(self.count)
        ]


class APITaskSource:
    def __init__(self, tasks: list[dict] | None = None):
        self._tasks = tasks or []
    
    def get_tasks(self) -> list[Task]:
        return [Task(id=item["id"], payload=item["payload"]) for item in self._tasks]
    
    def add_task(self, task_id: str, payload: Any) -> None:
        self._tasks.append({"id": task_id, "payload": payload})


def validation(source: Any) -> bool:
    return isinstance(source, TaskSource)


def collect_all(sources: list[Any]) -> list[Task]:
    result: list[Task] = []
    for source in sources:
        if not validation(source):
            error_msg = f"{type(source).__name__} не реализует контракт TaskSource"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        extracted_tasks = source.get_tasks()
        logger.info(f"Получено {len(extracted_tasks)} задач из {type(source).__name__}")
        result.extend(extracted_tasks)
    return result
