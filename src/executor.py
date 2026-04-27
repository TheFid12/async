import asyncio
import logging
from typing import Protocol, runtime_checkable

from src.task import Task, StatusEnum
from src.task_queue import TaskQueue

logger = logging.getLogger(__name__)

@runtime_checkable
class TaskHandler(Protocol):
    async def process(self, task: Task) -> None:
        ...


class DefaultHandler:
    async def process(self, task: Task) -> None:
        if task.status != StatusEnum.NOT_STARTED:
            raise ValueError("Задача уже выполняется или завершена.")
        
        task.status = StatusEnum.PROCESSING
        logger.info("Начата обработка %s (приоритет=%s)", task.id, task.priority)
        
        if not task.payload:
            task.status = StatusEnum.CANCELLED
            logger.warning("Отменена %s (empty payload)", task.id)
            return
            
        await asyncio.sleep(0.5)
        task.status = StatusEnum.COMPLETED
        logger.info("Завершена %s with payload: %s", task.id, task.payload)


class FastHandler:
    async def process(self, task: Task) -> None:
        if task.status != StatusEnum.NOT_STARTED:
            raise ValueError("Задача уже выполняется или завершена.")
        
        task.status = StatusEnum.PROCESSING
        logger.info("[FAST] Начата обработка %s", task.id)
        
        if not task.payload:
            task.status = StatusEnum.CANCELLED
            return
            
        await asyncio.sleep(0.1)
        task.status = StatusEnum.COMPLETED
        logger.info("[FAST] Завершена %s", task.id)


class TaskExecutor:
    def __init__(self, queue: TaskQueue, handler: TaskHandler) -> None:
        self.queue = queue
        self.handler = handler

    async def __aenter__(self):
        logger.info("Запуск контекста TaskExecutor...")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("Остановка контекста TaskExecutor...")
        if exc_type:
            logger.error("Исключение исполнителя: %s: %s", exc_type.__name__, exc_val)

    async def run(self) -> None:
        try:
            async for task in self.queue:
                try:
                    logger.debug("Извлечено из очереди %s", task.id)
                    await self.handler.process(task)
                except Exception as e:
                    logger.error("Ошибка при обработке %s: %s", task.id, str(e), exc_info=True)
                    task.status = StatusEnum.CANCELLED
                finally:
                    self.queue.task_done()
        except asyncio.ОтмененаError:
            logger.info("Выполнение TaskExecutor было отменено")

