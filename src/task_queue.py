from __future__ import annotations

import asyncio
from typing import AsyncIterator, Iterable, TYPE_CHECKING

PRIORITIES = ("низкий", "средний", "высокий", "критический")

if TYPE_CHECKING:
    from src.task import Task

class TaskQueue:
    def __init__(self, initial: Iterable["Task"] | None = None) -> None:
        self._queue: asyncio.Queue["Task" | None] = asyncio.Queue()
        if initial:
            for task in initial:
                self._queue.put_nowait(task)

    def __len__(self) -> int:
        return self._queue.qsize()

    def __aiter__(self) -> AsyncIterator["Task"]:
        return self

    async def __anext__(self) -> "Task":
        task = await self._queue.get()
        if task is None:
            self._queue.task_done()
            raise StopAsyncIteration
        return task

    async def enqueue(self, task: "Task") -> None:
        await self._queue.put(task)

    async def dequeue(self) -> "Task":
        if self._queue.empty():
            raise IndexError("Очередь пуста")
        task = await self._queue.get()
        if task is None:
            self._queue.task_done()
            raise IndexError("Очередь закрыта")
        return task

    async def signal_done(self) -> None:
        await self._queue.put(None)

    def task_done(self) -> None:
        self._queue.task_done()

    async def join(self) -> None:
        await self._queue.join()
