import random
import string
from datetime import datetime

import pendulum

from profiles.models import Name


def expires_at(expires_in: int) -> datetime:
    return pendulum.utcnow().add(seconds=expires_in)


def generate_random_string(length: int, chars: str = string.ascii_letters + string.digits) -> str:
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def remove_none_values(items: dict) -> dict:
    return dict(filter(lambda item: item[1] is not None, items.items()))


def string_to_name(name: str) -> Name:
    """Turns a string into a Name.
    This is rather naive and structured source data should be used instead.
    """
    return Name(*name.split(maxsplit=1))
