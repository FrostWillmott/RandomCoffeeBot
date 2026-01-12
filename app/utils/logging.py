"""Logging utilities."""

import logging
import sys


def setup_logging(level_name: str, fmt_type: str) -> None:
    """Configure global logging settings.

    Args:
        level_name: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        fmt_type: Format type ('json' or 'text')
    """
    log_level = getattr(logging, level_name.upper(), logging.INFO)

    if fmt_type == "json":
        from pythonjsonlogger.json import JsonFormatter

        from app.constants import LOG_FORMAT

        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(JsonFormatter(LOG_FORMAT))
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(log_handler)
    else:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
