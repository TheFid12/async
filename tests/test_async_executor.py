"""
Асинхронные тесты для проверки корректности работы системы обработки задач.
Демонстрируют асинхронность и отсутствие блокировок в event loop.
"""

import asyncio
import logging
import pytest
from src.task import Task, StatusEnum
from src.task_queue import TaskQueue
from src.executor import DefaultHandler, FastHandler, TaskExecutor

# Настройка логирования для тестов
logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
async def test_async_queue_iteration():
    """Тест асинхронной итерации по очереди задач."""
    # Создаем задачи
    tasks = [
        Task(id=1, payload="task1", priority="low"),
        Task(id=2, payload="task2", priority="medium"),
        Task(id=3, payload="task3", priority="high"),
    ]
    
    queue = TaskQueue(initial=tasks)
    await queue.signal_done()
    
    # Проверяем асинхронную итерацию
    collected = []
    async for task in queue:
        collected.append(task.id)
    
    assert collected == ["task_1", "task_2", "task_3"]


@pytest.mark.asyncio
async def test_task_status_transitions():
    """Тест переходов статусов задачи."""
    task = Task(id=1, payload="test", priority="medium")
    
    assert task.status == StatusEnum.NOT_STARTED
    task.status = StatusEnum.PROCESSING
    assert task.status == StatusEnum.PROCESSING
    task.status = StatusEnum.COMPLETED
    assert task.status == StatusEnum.COMPLETED


@pytest.mark.asyncio
async def test_default_handler_processing():
    """Тест асинхронной обработки задачи DefaultHandler."""
    handler = DefaultHandler()
    task = Task(id=1, payload="test", priority="low")
    
    # Обработка должна быть асинхронной и без блокировок
    start_time = asyncio.get_event_loop().time()
    await handler.process(task)
    end_time = asyncio.get_event_loop().time()
    
    assert task.status == StatusEnum.COMPLETED
    # Проверяем, что время выполнения соответствует asyncio.sleep(0.5)
    assert (end_time - start_time) >= 0.5


@pytest.mark.asyncio
async def test_fast_handler_processing():
    """Тест асинхронной обработки задачи FastHandler."""
    handler = FastHandler()
    task = Task(id=1, payload="test", priority="high")
    
    start_time = asyncio.get_event_loop().time()
    await handler.process(task)
    end_time = asyncio.get_event_loop().time()
    
    assert task.status == StatusEnum.COMPLETED
    # FastHandler быстрее, чем DefaultHandler
    assert (end_time - start_time) >= 0.1


@pytest.mark.asyncio
async def test_empty_payload_cancellation():
    """Тест отмены задачи с пустой полезной нагрузкой."""
    handler = DefaultHandler()
    task = Task(id=1, payload="", priority="low")
    
    await handler.process(task)
    assert task.status == StatusEnum.CANCELLED


@pytest.mark.asyncio
async def test_executor_context_manager():
    """Тест контекстного менеджера TaskExecutor."""
    tasks = [
        Task(id=1, payload="task1", priority="low"),
        Task(id=2, payload="task2", priority="medium"),
    ]
    queue = TaskQueue(initial=tasks)
    await queue.signal_done()
    
    handler = DefaultHandler()
    async with TaskExecutor(queue, handler) as executor:
        assert executor is not None
        await executor.run()
    
    # После выполнения все задачи должны быть обработаны
    assert tasks[0].status == StatusEnum.COMPLETED
    assert tasks[1].status == StatusEnum.COMPLETED


@pytest.mark.asyncio
async def test_sequential_async_processing():
    """Тест последовательной асинхронной обработки задач."""
    tasks = [
        Task(id=i, payload=f"payload_{i}", priority="medium")
        for i in range(1, 4)
    ]
    
    queue = TaskQueue(initial=tasks)
    await queue.signal_done()
    
    processed_order = []
    
    class LoggingHandler:
        async def process(self, task: Task):
            processed_order.append(task.id)
            task.status = StatusEnum.PROCESSING
            await asyncio.sleep(0.1)
            task.status = StatusEnum.COMPLETED
    
    handler = LoggingHandler()
    async with TaskExecutor(queue, handler) as executor:
        await executor.run()
    
    # Задачи обрабатывались в порядке очереди
    assert processed_order == ["task_1", "task_2", "task_3"]
    # Все задачи завершены
    assert all(t.status == StatusEnum.COMPLETED for t in tasks)


@pytest.mark.asyncio
async def test_error_handling_in_executor():
    """Тест обработки ошибок внутри исполнителя."""
    tasks = [
        Task(id=1, payload="task1", priority="low"),
        Task(id=2, payload="", priority="medium"),  # Вызовет отмену
        Task(id=3, payload="task3", priority="high"),
    ]
    
    queue = TaskQueue(initial=tasks)
    await queue.signal_done()
    
    handler = DefaultHandler()
    async with TaskExecutor(queue, handler) as executor:
        await executor.run()
    
    # Первая задача выполнена
    assert tasks[0].status == StatusEnum.COMPLETED
    # Вторая задача отменена (пустой payload)
    assert tasks[1].status == StatusEnum.CANCELLED
    # Третья задача выполнена
    assert tasks[2].status == StatusEnum.COMPLETED


@pytest.mark.asyncio
async def test_concurrent_like_async_execution():
    """
    Тест асинхронного выполнения задач.
    Демонстрирует асинхронность - задачи не блокируют друг друга.
    """
    tasks = [
        Task(id=i, payload=f"payload_{i}", priority="high")
        for i in range(1, 4)
    ]
    
    queue = TaskQueue(initial=tasks)
    await queue.signal_done()
    
    start_time = asyncio.get_event_loop().time()
    handler = DefaultHandler()
    async with TaskExecutor(queue, handler) as executor:
        await executor.run()
    end_time = asyncio.get_event_loop().time()
    
    # Хотя каждая задача спит 0.5 сек, они выполняются последовательно
    # поэтому общее время должно быть около 1.5 сек или больше
    total_time = end_time - start_time
    assert total_time >= 1.4  # Примерно 3 * 0.5
    assert all(t.status == StatusEnum.COMPLETED for t in tasks)


@pytest.mark.asyncio
async def test_queue_enqueue_dequeue():
    """Тест добавления и извлечения задач из асинхронной очереди."""
    queue = TaskQueue()
    
    task1 = Task(id=1, payload="first", priority="low")
    task2 = Task(id=2, payload="second", priority="high")
    
    await queue.enqueue(task1)
    await queue.enqueue(task2)
    
    dequeued1 = await queue.dequeue()
    dequeued2 = await queue.dequeue()
    
    assert dequeued1.id == "task_1"
    assert dequeued2.id == "task_2"


@pytest.mark.asyncio
async def test_priority_attribute():
    """Тест установки приоритета задачи."""
    task = Task(id=1, payload="test", priority="high")
    assert task.priority == "high"
    
    # Изменение приоритета
    task.priority = "CRITICAL"
    assert task.priority == "critical"
    
    # Недопустимый приоритет
    with pytest.raises(ValueError):
        task.priority = "invalid_priority"


@pytest.mark.asyncio
async def test_handler_protocol_compliance():
    """Тест соответствия обработчиков протоколу TaskHandler."""
    from src.executor import TaskHandler
    
    handler1 = DefaultHandler()
    handler2 = FastHandler()
    
    # Проверяем, что оба обработчика соответствуют протоколу
    assert isinstance(handler1, TaskHandler)
    assert isinstance(handler2, TaskHandler)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
