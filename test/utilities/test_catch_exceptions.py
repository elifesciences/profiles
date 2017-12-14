import logging
from logging import Handler, Logger, Manager
from logging.handlers import BufferingHandler

from pytest import fixture

from profiles.utilities import catch_exceptions


@fixture
def logger(handler: Handler) -> Logger:
    logger = Logger('logger', logging.DEBUG)
    logger.addHandler(handler)
    logger.manager = Manager('root')

    return logger


@fixture
def handler() -> Handler:
    return BufferingHandler(100)


def test_it_catches_and_logs_exceptions(logger: Logger, handler: BufferingHandler):
    @catch_exceptions(logger)
    def my_function():
        raise Exception('My exception')

    result = my_function()

    assert result is None
    assert len(handler.buffer) == 1


def test_it_does_nothing_when_no_exception(logger: Logger, handler: BufferingHandler):
    @catch_exceptions(logger)
    def my_function():
        return True

    result = my_function()

    assert result is True
    assert len(handler.buffer) == 0
