import asyncio
import logging
from pathlib import Path

import typer

from src.handler import collect_and_process
from src.source import ApiSource, FileSource, GeneratorSource, Source
from src.task import StatusEnum

app = typer.Typer(help="CLI утилита для асинхронного выполнения задач.")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
    generator_count: int = typer.Option(5, "--generator-count", "-g", help="Количество генерируемых задач"),
    file_path: str | None = typer.Option(None, "--file", "-f", help="Путь к JSON файлу с задачами"),
    api_payload: list[str] = typer.Option(
        None, "--api", "-a", help="Полезная нагрузка API задачи: -a task1 -a task2"
    ),
) -> None:
    configure_logging()
    api_payload = api_payload or []
    sources = build_sources(generator_count, file_path, api_payload)

    if not sources:
        typer.echo("Ошибка: Пожалуйста, укажите хотя бы один источник данных.")
        raise typer.Exit(code=1)

    tasks = asyncio.run(collect_and_process(sources))
    
    completed = sum(1 for t in tasks if t.status == StatusEnum.COMPLETED)
    cancelled = sum(1 for t in tasks if t.status == StatusEnum.CANCELLED)
    
    typer.echo(f"\nИтоги выполнения: {len(tasks)} обработано.")
    typer.echo(f"  - Завершена: {completed}")
    typer.echo(f"  - Отменена: {cancelled}")


if __name__ == '__main__':
    app()
