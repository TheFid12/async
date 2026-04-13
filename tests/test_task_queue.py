import pytest

from src.task import StatusEnum, Task, TaskQueue


def make_queue() -> TaskQueue:
    first = Task(1, "first", priority="low")
    second = Task(2, "second", priority="high")
    third = Task(3, "third", priority="high")
    second.status = StatusEnum.PROCESSING
    third.status = StatusEnum.PROCESSING
    return TaskQueue([first, second, third])


def test_queue_supports_repeat_iteration():
    queue = make_queue()
    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]
    assert first_pass == ["task_1", "task_2", "task_3"]
    assert second_pass == first_pass


def test_queue_iterator_raises_stop_iteration():
    queue = TaskQueue([Task(1, "only")])
    iterator = iter(queue)
    assert next(iterator).id == "task_1"
    with pytest.raises(StopIteration):
        next(iterator)


def test_lazy_filters_by_status_and_priority():
    queue = make_queue()
    by_status = queue.filter_by_status(StatusEnum.PROCESSING)
    by_priority = queue.filter_by_priority("HIGH")
    assert [task.id for task in by_status] == ["task_2", "task_3"]
    assert [task.id for task in by_priority] == ["task_2", "task_3"]


def test_filter_is_lazy_generator():
    queue = make_queue()
    stream = queue.filter(lambda task: task.priority == "high")
    assert iter(stream) is stream
    assert next(stream).id == "task_2"


def test_stream_processes_without_intermediate_collection():
    queue = TaskQueue([Task(1, 2), Task(2, 3), Task(3, 4)])
    result = TaskQueue.stream(queue, lambda task: task.payload * 10)
    assert list(result) == [20, 30, 40]
