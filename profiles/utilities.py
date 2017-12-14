import json
import os
import random
import string
from datetime import datetime
from functools import wraps
from logging import Logger
from typing import Any, Callable

from elife_api_validator import SCHEMA_DIRECTORY
from flask import request
from jsonschema import SchemaError, ValidationError, validate
import pendulum
from werkzeug.wrappers import Response

from profiles.exceptions import SchemaNotFound


def catch_exceptions(logger: Logger) -> Callable[..., Any]:
    def outer_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except BaseException as exception:
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


def validate_json(data: dict, schema_name: str, schema_dir: str = ''):
    # option to provide a schema_dir allows dummy_schema to be found for tests,
    # this whole function will be removed and replaced with
    # api-validator-python functionality
    schema_dir = schema_dir or SCHEMA_DIRECTORY

    schema_path = os.path.join(schema_dir, '{}.json'.format(schema_name))

    try:
        with open(schema_path) as schema_file:
            validate(data, schema=json.load(schema_file))
        return True
    except FileNotFoundError:

        raise SchemaNotFound('Could not find schema {}'.format(schema_path))
    except (SchemaError, ValidationError):
        # Need to re raise with schema/validation failure information,
        # though as this will be replaced by api-validator-python
        # leaving for now
        return False
