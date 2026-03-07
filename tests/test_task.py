import pytest
from src.task import Task


def test_task_creation():
    task = Task(id='task_1', payload='test data')
    assert task.id == 'task_1'
    assert task.payload == 'test data'


def test_task_with_dict_payload():
    task = Task(id='task_2', payload={'key': 'value', 'num': 42})
    assert task.id == 'task_2'
    assert task.payload['key'] == 'value'
    assert task.payload['num'] == 42


def test_task_with_list_payload():
    task = Task(id='task_3', payload=[1, 2, 3])
    assert task.id == 'task_3'
    assert task.payload == [1, 2, 3]


def test_task_equality():
    task1 = Task(id='task_1', payload='data')
    task2 = Task(id='task_1', payload='data')
    assert task1 == task2


def test_task_inequality():
    task1 = Task(id='task_1', payload='data')
    task2 = Task(id='task_2', payload='data')
    assert task1 != task2
