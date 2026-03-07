import pytest
import json
from pathlib import Path
from typing import Any

from src.task import Task
from src.source import (
    TaskSource,
    FileTaskSource,
    GeneratorTaskSource,
    APITaskSource,
    validation,
    collect_all_tasks,
)


class MockTaskSource:
    def get_tasks(self):
        return [Task(id='mock_1', payload='mock data')]


class InvalidSource:
    def get_items(self):
        return []


def test_task_source_protocol_validation():
    source = MockTaskSource()
    assert isinstance(source, TaskSource)


def test_invalid_source_not_matching_protocol():
    source = InvalidSource()
    assert not isinstance(source, TaskSource)


def test_file_task_source_reads_json(tmp_path):
    file_path = tmp_path / 'tasks.json'
    data = [
        {'id': 'file_1', 'payload': 'data 1'},
        {'id': 'file_2', 'payload': 'data 2'}
    ]
    file_path.write_text(json.dumps(data))
    
    source = FileTaskSource(str(file_path))
    tasks = source.get_tasks()
    
    assert len(tasks) == 2
    assert tasks[0].id == 'file_1'
    assert tasks[0].payload == 'data 1'
    assert tasks[1].id == 'file_2'
    assert tasks[1].payload == 'data 2'


def test_file_task_source_empty_file(tmp_path):
    file_path = tmp_path / 'empty.json'
    file_path.write_text('[]')
    
    source = FileTaskSource(str(file_path))
    tasks = source.get_tasks()
    
    assert len(tasks) == 0


def test_file_task_source_nonexistent_file(tmp_path):
    file_path = tmp_path / 'nonexistent.json'
    source = FileTaskSource(str(file_path))
    tasks = source.get_tasks()
    
    assert len(tasks) == 0


def test_generator_task_source_creates_tasks():
    source = GeneratorTaskSource(count=5, prefix='test')
    tasks = source.get_tasks()
    
    assert len(tasks) == 5
    assert tasks[0].id == 'test_0'
    assert tasks[4].id == 'test_4'
    assert 'Generated task' in tasks[0].payload


def test_generator_task_source_zero_count():
    source = GeneratorTaskSource(count=0)
    tasks = source.get_tasks()
    
    assert len(tasks) == 0


def test_generator_task_source_default_prefix():
    source = GeneratorTaskSource(count=3)
    tasks = source.get_tasks()
    
    assert tasks[0].id == 'gen_0'


def test_api_task_source_empty():
    source = APITaskSource()
    tasks = source.get_tasks()
    
    assert len(tasks) == 0


def test_api_task_source_with_initial_tasks():
    initial_tasks = [
        {'id': 'api_1', 'payload': 'api data 1'},
        {'id': 'api_2', 'payload': 'api data 2'}
    ]
    source = APITaskSource(tasks=initial_tasks)
    tasks = source.get_tasks()
    
    assert len(tasks) == 2
    assert tasks[0].id == 'api_1'
    assert tasks[1].payload == 'api data 2'


def test_api_task_source_add_task():
    source = APITaskSource()
    source.add_task('new_1', 'new data')
    tasks = source.get_tasks()
    
    assert len(tasks) == 1
    assert tasks[0].id == 'new_1'
    assert tasks[0].payload == 'new data'


def test_api_task_source_add_multiple_tasks():
    source = APITaskSource()
    source.add_task('task_1', 'data 1')
    source.add_task('task_2', 'data 2')
    source.add_task('task_3', 'data 3')
    tasks = source.get_tasks()
    
    assert len(tasks) == 3


def test_validate_task_source_valid():
    source = GeneratorTaskSource(count=1)
    assert validation(source) is True


def test_validate_task_source_invalid():
    source = InvalidSource()
    assert validation(source) is False


def test_collect_all_tasks_valid():
    source = GeneratorTaskSource(count=3)
    tasks = collect_all_tasks([source])

    assert len(tasks) == 3


def test_collect_all_tasks_invalid():
    source = InvalidSource()

    with pytest.raises(TypeError, match='не реализует контракт'):
        collect_all_tasks([source])


def test_all_sources_match_protocol():
    file_source = FileTaskSource('dummy.json')
    gen_source = GeneratorTaskSource(count=1)
    api_source = APITaskSource()
    
    assert isinstance(file_source, TaskSource)
    assert isinstance(gen_source, TaskSource)
    assert isinstance(api_source, TaskSource)


def test_file_task_source_with_complex_payload(tmp_path):
    file_path = tmp_path / 'complex.json'
    data = [
        {'id': 'complex_1', 'payload': {'nested': {'value': 42}, 'list': [1, 2, 3]}}
    ]
    file_path.write_text(json.dumps(data))
    
    source = FileTaskSource(str(file_path))
    tasks = source.get_tasks()
    
    assert tasks[0].payload['nested']['value'] == 42
    assert tasks[0].payload['list'] == [1, 2, 3]
