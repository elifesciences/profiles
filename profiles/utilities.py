import random
import string
from datetime import datetime, timedelta, timezone


def expires_at(expires_in: int) -> datetime:
    return (datetime.utcnow() + timedelta(seconds=expires_in)).replace(tzinfo=timezone.utc)


def generate_random_string(length: int, chars: str = string.ascii_letters + string.digits) -> str:
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def remove_none_values(items: dict) -> dict:
    return dict(filter(lambda item: item[1] is not None, items.items()))
