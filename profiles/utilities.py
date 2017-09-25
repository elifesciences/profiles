import random
import string
from datetime import datetime

import pendulum


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
