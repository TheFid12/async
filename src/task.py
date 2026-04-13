from datetime import datetime
from enum import Enum
from typing import Any
from src.task_queue import TaskQueue


class StatusEnum(Enum):
    NOT_STARTED = "Not started"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


PRIORITIES = ("low", "medium", "high", "critical")


class Task:
    __slots__ = ("_num_id", "_priority", "_status", "_created_at", "payload")

    def __init__(self, id: int, payload: Any, priority: str = "medium") -> None:
        self._num_id = int(id)
        self.payload = payload
        self._created_at = datetime.now()
        self._status = StatusEnum.NOT_STARTED
        self.priority = priority

    @staticmethod
    def format_id(task_id: int) -> str:
        return f"task_{task_id}"

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, payload={self.payload!r}, priority={self.priority!r}, "
            f"status={self.status.value!r}, time_created={self.time_created!s})"
        )

    __str__ = __repr__

    @property
    def id(self) -> str:
        return Task.format_id(self._num_id)

    @property
    def time_created(self) -> datetime:
        return self._created_at

    @property
    def priority(self) -> str:
        return self._priority

    @priority.setter
    def priority(self, value: str) -> None:
        if isinstance(value, str):
            priority = value.strip().lower()
        else:
            priority = str(value).lower()

        if priority not in PRIORITIES:
            raise ValueError(f"Недопустимый приоритет. Доступные: {PRIORITIES}")
        self._priority = priority

    @property
    def status(self) -> StatusEnum:
        return self._status

    @status.setter
    def status(self, value: StatusEnum) -> None:
        if self._status in (StatusEnum.CANCELLED, StatusEnum.COMPLETED):
            raise ValueError(f"Нельзя менять статус {self._status}")
        if value == StatusEnum.NOT_STARTED and self._status != StatusEnum.NOT_STARTED:
            raise ValueError(f"Нельзя поменять статус {self._status} на {StatusEnum.NOT_STARTED}")
        self._status = value


__all__ = ["StatusEnum", "PRIORITIES", "Task", "TaskQueue"]
