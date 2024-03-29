import logging
import os
import traceback
from typing import List

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def formatException(self, ei: List) -> dict:
        info_type, info_value, info_traceback = ei
        return {
            'message': info_value,
            'class': info_type.__name__,
            'trace': traceback.format_tb(info_traceback),
        }


def configure_logging(env: str = 'dev', level: int = logging.INFO, path: str = None) -> None:
    logging.getLogger().setLevel(level)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    logging.getLogger().addHandler(console_handler)

    if path:
        log_filename = os.path.abspath(os.path.join(
            path,
            '%s.json.log' % env
        ))
        os.makedirs(path, exist_ok=True)

        file_handler = logging.FileHandler(filename=log_filename)
        file_handler.setLevel(level)
        formatter = CustomJsonFormatter('%(name)s %(message)s %(asctime)s %(levelname)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
