"""Logging configuration for the trading bot."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_file: str = "logs.txt") -> None:
    project_root = Path(__file__).resolve().parents[1]
    log_path = project_root / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    has_file_handler = False
    has_console_handler = False

    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler) and getattr(handler, "baseFilename", "") == str(log_path):
            has_file_handler = True
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            has_console_handler = True

    if not has_file_handler:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if not has_console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
