import logging
import random
from src.task import Task, StatusEnum, PRIORITIES
from src.source import Source

logger = logging.getLogger(__name__)

def process_task(task: Task) -> None:
    """
    Обработчик задачи. Переводит статусы и печатает результат.
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
