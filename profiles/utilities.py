import random
import string
from typing import Type


def chain_exception(exception: Type[Exception], previous: Exception, message: str = None):
    exception = exception(message or str(previous))
    exception.__cause__ = previous
    return exception


def generate_id() -> str:
    return generate_random_string(8, string.ascii_lowercase + string.digits)


def generate_random_string(size: int, chars: str) -> str:
    return ''.join(random.choices(chars, k=size))


def remove_none_values(items: dict) -> dict:
    return dict(filter(lambda item: item[1] is not None, items.items()))
