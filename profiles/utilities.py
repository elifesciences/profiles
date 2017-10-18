import json
import os
import random
import string
from datetime import datetime

from jsonschema import SchemaError, ValidationError, validate
import pendulum
from profiles.exceptions import SchemaNotFound


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


def validate_json(data: dict, schema_name: str):
    schema_dir = 'test/schema'  # Will be replaced with elife_api.schema_directory

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
