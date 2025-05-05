"""
Модуль логгирования для проекта.

Этот модуль предоставляет функцию `setup_logging` для централизованной настройки логирования.
Логгер настраивается один раз и возвращается при повторных вызовах.
"""

import logging


def setup_logging(level=logging.INFO, log_file="app.log"):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )
