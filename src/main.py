import logging
from pathlib import Path

import typer

from src.handler import collect_all
from src.source import ApiSource, FileSource, GeneratorSource, Source
from src.task import StatusEnum, TaskQueue

app = typer.Typer(help="CLI для лабораторной №3: очередь задач и ленивые генераторы.")


def configure_logging() -> None:
    logging.basicConfig(
        filename="log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )


def build_sources(
    generator_count: int, file_path: str | None, api_payload: list[str]
) -> list[Source]:
    sources: list[Source] = []
    if generator_count > 0:
        sources.append(GeneratorSource(count=generator_count))
    if file_path:
        sources.append(FileSource(file_path))
    if api_payload:
        sources.append(ApiSource(tasks=[{"payload": item} for item in api_payload]))
    return sources


@app.command("run")
def run_command(
    generator_count: int = typer.Option(0, "--generator-count", "-g"),
    file_path: str | None = typer.Option(None, "--file", "-f"),
    api_payload: list[str] = typer.Option(
        None, "--api", "-a", help="Повторяйте опцию: -a task1 -a task2"
    ),
) -> None:
    """Собрать задачи из источников и обработать их."""
    configure_logging()
    sources = build_sources(generator_count, file_path, api_payload or [])

    if not sources:
        typer.echo("Не выбрано ни одного источника. Добавьте хотя бы один.")
        raise typer.Exit(code=1)

    tasks = collect_all(sources)
    queue = TaskQueue(tasks)
    typer.echo(f"Обработано задач: {len(queue)}")


@app.command("filter")
def filter_command(
    by_status: StatusEnum | None = typer.Option(None, "--status"),
    by_priority: str | None = typer.Option(None, "--priority"),
    file_path: str = typer.Option("tasks.json", "--file", "-f"),
) -> None:
    """Показать задачи по ленивым фильтрам."""
    configure_logging()
    if not Path(file_path).exists():
        typer.echo(f"Файл не найден: {file_path}")
        raise typer.Exit(code=1)

    tasks = collect_all([FileSource(file_path)])
    queue = TaskQueue(tasks)

    filtered = iter(queue)
    if by_status is not None:
        filtered = queue.filter_by_status(by_status)
    if by_priority is not None:
        base_iter = filtered if by_status is not None else iter(queue)
        filtered = (task for task in base_iter if task.priority == by_priority.lower())

    for task in filtered:
        typer.echo(str(task))


def main() -> None:
    configure_logging()
    demo_sources = [GeneratorSource(count=1, prefix="demo"), ApiSource([{"payload": "api data"}])]
    collect_all(demo_sources)


if __name__ == "__main__":
    app()
