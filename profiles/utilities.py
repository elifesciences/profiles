from typing import Type


def chain_exception(exception: Type[Exception], previous: Exception, message: str = None):
    exception = exception(message or str(previous))
    exception.__cause__ = previous
    return exception


def remove_none_values(items: dict) -> dict:
    return dict(filter(lambda item: item[1] is not None, items.items()))
