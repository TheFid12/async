import pytest
import json
from src.task import StatusEnum
from src.source import Source, FileSource, GeneratorSource, ApiSource, collect_all

def test_source_protocol():
    assert isinstance(GeneratorSource(2), Source)
    assert isinstance(FileSource("tasks.json"), Source)
    assert isinstance(ApiSource(), Source)

def test_generator_source():
    src = GeneratorSource(2, "gen")
    tasks = src.get_tasks()
    assert len(tasks) == 2
    assert "gen" in tasks[0]

def test_file_source(tmp_path):
    file_path = tmp_path / "tasks.json"
    file_path.write_text(json.dumps([{"payload": "data 1"}]))
    src = FileSource(str(file_path))
    assert src.get_tasks() == ["data 1"]

def test_api_source():
    src = ApiSource([{"payload": "data"}])
    assert src.get_tasks() == ["data"]

def test_collect_all():
    sources = [GeneratorSource(count=1), ApiSource([{"payload": "test"}])]
    tasks = collect_all(sources)
    
    assert len(tasks) == 2
    assert tasks[0].id == "task_1"
    assert tasks[1].id == "task_2"
    assert tasks[0].status == StatusEnum.COMPLETED

def test_collect_all_invalid_source():
    class BadSource:
        pass
    
    with pytest.raises(TypeError):
        collect_all([BadSource()])

