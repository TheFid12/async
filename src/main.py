import logging
from src.source import FileSource, GeneratorSource, ApiSource, collect_all

def main() -> None:
    """
    Запуск сборщика задач, который запрашивает и выполняет задачи
    из различных источников.
    """
    logging.basicConfig(
        filename="log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    sources = [
        GeneratorSource(count=3),
        FileSource("tasks.json"),
        ApiSource([{"payload": "api data"}])
    ]
    
    collect_all(sources)

if __name__ == "__main__":
    main()
