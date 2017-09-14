import random


def generate_random_string(size: int, chars: str) -> str:
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def remove_none_values(items: dict) -> dict:
    return dict(filter(lambda item: item[1] is not None, items.items()))
