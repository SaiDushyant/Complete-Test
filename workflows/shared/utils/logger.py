"""
Standardized Test Logger.
Provides structured and synchronized logging with timestamps and portal tags.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str = "workflow_test", level: int = logging.INFO) -> logging.Logger:
    """
    Returns a configured logger instance with formatted console output.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
