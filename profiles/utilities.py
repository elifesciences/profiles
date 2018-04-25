import random
import string
from datetime import datetime
from functools import wraps
from logging import Logger
from typing import Any, Callable

from flask import request
import pendulum
from werkzeug.wrappers import Response


def catch_exceptions(logger: Logger) -> Callable[..., Any]:
    def outer_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exception:  # pylint: disable=broad-except
                logger.exception(exception)

        return wrapper

    return outer_wrapper


def cache(allow_revalidation: bool = True) -> Callable[..., Response]:
    def outer_wrapper(func: Callable[..., Response]) -> Callable[..., Response]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Response:
            response = func(*args, **kwargs)
            response.headers['Cache-Control'] = 'max-age=300, public, stale-if-error=86400,' \
                                                'stale-while-revalidate=300'
            if allow_revalidation:
                response.add_etag()
                response.make_conditional(request)

            return response
        return wrapper

    return outer_wrapper


def no_cache(func: Callable[..., Response]) -> Callable[..., Response]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        response = func(*args, **kwargs)
        response.headers['Cache-Control'] = 'must-revalidate, no-cache, no-store, private'

        return response

    return wrapper


def expires_at(expires_in: int) -> datetime:
    return pendulum.utcnow().add(seconds=expires_in)


def generate_random_string(length: int, chars: str = string.ascii_letters + string.digits) -> str:
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def guess_index_name(name: str) -> str:
    """Guess index name for a preferred name.
    Naive calculation of "Family Name, Given Name"
    """
    return ', '.join(list(reversed(name.split(maxsplit=1))))


def remove_none_values(items: dict) -> dict:
    return dict(filter(lambda item: item[1] is not None, items.items()))
