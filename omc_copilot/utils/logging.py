from __future__ import annotations

import logging
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def set_level(level_name: Optional[str]) -> None:
    if not level_name:
        return
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.getLogger().setLevel(level)
