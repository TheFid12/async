import asyncio
import logging
import random
from src.task import Task, StatusEnum, PRIORITIES
from src.source import Source
from src.task_queue import TaskQueue
from src.executor import DefaultHandler, TaskExecutor

logger = logging.getLogger(__name__)

async def collect_and_process(sources: list[Source]) -> list[Task]:
    tasks: list[Task] = []
    logger.info("Начало сбора задач из переданных источников...")
    
    for source in sources:
        if not isinstance(source, Source):
            logger.error("Недопустимый тип источника: %s", type(source).__name__)
            raise TypeError("Источник должен строго соответствовать типу Source.")
            
        logger.info("Сбор из: %s", type(source).__name__)
        
        for payload in source.get_tasks():
            priority = random.choice(PRIORITIES)
            task = Task(id=len(tasks) + 1, payload=payload, priority=priority)
            tasks.append(task)
            logger.debug("Создана %s (приоритет=%s)", task.id, priority)
            
    logger.info("Собрано %d задач. Переход к фазе выполнения...", len(tasks))
    
    queue = TaskQueue(initial=tasks)
    await queue.signal_done()
    
    async with TaskExecutor(queue, DefaultHandler()) as executor:
        await executor.run()
        
    logger.info("Все ветви выполнения завершены без ошибок.")
    return tasks
