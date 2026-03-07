from src.source import (
    FileTaskSource,
    GeneratorTaskSource,
    APITaskSource,
    collect_all_tasks,
)


def main() -> None:
    """
    Точка входа в модуль.
    В sources указываются источники задач.
    """
    sources = [
        FileTaskSource("tasks.json"),
        GeneratorTaskSource(count=3, prefix="task"),
        APITaskSource([{"id": "api_task_1", "payload": "from api"}])
    ]

    tasks = collect_all_tasks(sources)

    for task in tasks:
        print(f"[{task.id}] {task.payload}")


if __name__ == "__main__":
    main()
