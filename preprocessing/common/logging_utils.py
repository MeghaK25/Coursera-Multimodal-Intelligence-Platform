import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from preprocessing.common.config import settings

_configured = False

# Force UTF-8 on Windows to avoid CP1252 encoding errors with Rich
_console = Console(stderr=True, force_terminal=False, highlight=False)


def _configure_logging() -> None:
    global _configured
    if _configured:
        return

    level = getattr(logging, settings.log_level, logging.INFO)

    handlers: list[logging.Handler] = [
        RichHandler(rich_tracebacks=True, show_path=False, console=_console)
    ]

    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_logging()
    return logging.getLogger(name)
