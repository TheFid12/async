from __future__ import annotations

from collections import deque
from typing import Any, Callable, Iterable, Iterator, TYPE_CHECKING

PRIORITIES = ("low", "medium", "high", "critical")

if TYPE_CHECKING:
    from src.task import StatusEnum, Task


class _QueueIterator(Iterator["Task"]):
    def __init__(self, tasks: tuple["Task", ...]) -> None:
        self._tasks = tasks
        self._index = 0

    def __iter__(self) -> "_QueueIterator":
        return self

    def __next__(self) -> "Task":
        if self._index >= len(self._tasks):
            raise StopIteration
        item = self._tasks[self._index]
        self._index += 1
        return item


class TaskQueue(Iterable["Task"]):
    def __init__(self, initial: Iterable["Task"] | None = None) -> None:
        self._queue = deque(initial or ())

    def __len__(self) -> int:
        return len(self._queue)

    def __iter__(self) -> Iterator["Task"]:
        return _QueueIterator(tuple(self._queue))

    def enqueue(self, task: "Task") -> None:
        self._queue.append(task)

    def dequeue(self) -> "Task":
        if not self._queue:
            raise IndexError("Очередь пуста")
        return self._queue.popleft()

    def where(self, matcher: Callable[["Task"], bool]) -> Iterator["Task"]:
        for task in self:
            if matcher(task):
                yield task

    filter = where

    def filter_by_status(self, status: "StatusEnum") -> Iterator["Task"]:
        yield from self.where(lambda task: task.status == status)

    def filter_by_priority(self, priority: str) -> Iterator["Task"]:
        normalized = str(priority).lower()
        if normalized not in PRIORITIES:
            raise ValueError(f"Недопустимый приоритет. Доступные: {PRIORITIES}")
        yield from self.where(lambda task: task.priority == normalized)

    @staticmethod
    def stream(
        tasks: Iterable["Task"], processor: Callable[["Task"], Any]
    ) -> Iterator[Any]:
        for task in tasks:
            yield processor(task)
