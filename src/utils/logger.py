# src/utils/logger.py

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def _make_formatter(service_name: str):
    fmt = "%(asctime)s [%(levelname)s] [%(service)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    return logging.Formatter(fmt=fmt, datefmt=datefmt)


def setup_logger(service_name: str = "app", level: int = logging.INFO):
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(service_name)
    logger.setLevel(level)

    if logger.handlers:
        return logging.LoggerAdapter(logger, {"service": service_name})

    # File handler with rotation
    fh = RotatingFileHandler(f"logs/{service_name}.log", maxBytes=10_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(_make_formatter(service_name))

    # Stream handler (stdout)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(_make_formatter(service_name))

    logger.addHandler(fh)
    logger.addHandler(sh)

    # Return a LoggerAdapter so every record has 'service' field
    return logging.LoggerAdapter(logger, {"service": service_name})