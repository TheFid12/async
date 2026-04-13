from typing import Protocol, runtime_checkable, Any
import json
import logging
from pathlib import Path

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


from src.handler import collect_all, process_task

