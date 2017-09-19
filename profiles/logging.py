import logging
import os


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
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)
