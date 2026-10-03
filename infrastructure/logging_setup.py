"""Structured JSON logging for Flask (self-hosted / local server)."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    """One JSON object per line — easy to grep / pipe into AI analysis."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in (
            "request_id",
            "user_id",
            "method",
            "path",
            "status",
            "error_code",
            "duration_ms",
            "remote_addr",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def log_dir() -> Path:
    raw = os.getenv("LOG_DIR", "logs")
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_file_path() -> Path:
    name = os.getenv("LOG_FILE", "app.log")
    return log_dir() / name


def configure_logging(*, testing: bool = False) -> logging.Logger:
    """Configure root app logger. Idempotent for create_app re-entry in pytest."""
    level_name = os.getenv("LOG_LEVEL", "DEBUG" if testing else "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logger = logging.getLogger("qa_assistant")
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter: logging.Formatter
    if os.getenv("LOG_JSON", "1").strip() != "0":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    stream.setLevel(level)
    logger.addHandler(stream)

    if not testing and os.getenv("LOG_TO_FILE", "1").strip() != "0":
        file_handler = RotatingFileHandler(
            log_file_path(),
            maxBytes=int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024))),
            backupCount=int(os.getenv("LOG_BACKUP_COUNT", "3")),
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("qa_assistant")
