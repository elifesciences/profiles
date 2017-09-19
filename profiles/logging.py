import logging
import os
import sys
import traceback

from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def formatException(self, exc_info):
        t, v, tb = sys.exc_info()
        return {
            'message': v,
            'class': t.__name__,
            'trace': traceback.format_tb(tb),
        }

def configure_logging(env='dev', level=logging.INFO, path=None) -> None:
    logging.getLogger().setLevel(level)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    logging.getLogger().addHandler(console_handler)

    if path:
        log_filename = os.path.abspath(os.path.join(
            path,
            '%s.log' % env
        ))

        file_handler = logging.FileHandler(filename=log_filename)
        file_handler.setLevel(level)
        formatter = CustomJsonFormatter('(message) (asctime) (levelname)')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
