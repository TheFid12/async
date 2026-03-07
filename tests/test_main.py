import pytest

from src.source import (
    GeneratorTaskSource,
    APITaskSource,
    collect_all_tasks,
)
from src.main import main


class BrokenSource:
    def get_items(self):
        return []


def test_collect_all_tasks_multiple_sources():
    gen = GeneratorTaskSource(count=2, prefix="t")
    api = APITaskSource(tasks=[{"id": "a1", "payload": "data"}])

    result = collect_all_tasks([gen, api])

    assert len(result) == 3
    assert result[0].id == "t_0"
    assert result[2].id == "a1"


def test_collect_all_tasks_empty():
    assert collect_all_tasks([]) == []


def test_collect_all_tasks_rejects_invalid():
    broken = BrokenSource()

    with pytest.raises(TypeError, match="не реализует контракт"):
        collect_all_tasks([broken])


def test_main_output(capsys):
    main()
    output = capsys.readouterr().out

    assert "task_0" in output
    assert "api_task_1" in output
    assert "from api" in output
