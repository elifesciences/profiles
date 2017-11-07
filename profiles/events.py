from typing import Callable

from elife_bus_sdk.events import ProfileEvent
from elife_bus_sdk.publishers import EventPublisher
from flask import Flask

from profiles.exceptions import UpdateEventFailure
from profiles.models import Profile


def send_update_events(publisher: EventPublisher) -> Callable[..., None]:
    def wrapper(sender: Flask, changes: tuple) -> None:  # pylint:disable=unused-argument
        for instance, operation in changes:
            if isinstance(instance, Profile):
                try:
                    # send message to bus indicating a profile change
                    publisher.publish(ProfileEvent(id=instance.id))
                except (AttributeError, RuntimeError):
                    raise UpdateEventFailure('Failed to send {0} '
                                             'event for Profile {1}'.format(instance, operation))

    return wrapper
