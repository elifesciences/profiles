import logging
from typing import Callable

from elife_bus_sdk.events import ProfileEvent
from elife_bus_sdk.publishers import EventPublisher
from flask import Flask

from profiles.exceptions import UpdateEventFailure
from profiles.models import Affiliation, EmailAddress, Profile


LOGGER = logging.getLogger(__name__)


def send_update_events(publisher: EventPublisher) -> Callable[..., None]:
    def wrapper(sender: Flask, changes: tuple) -> None:  # pylint:disable=unused-argument
        ids = []

        for instance, operation in changes:  # pylint:disable=unused-variable
            if isinstance(instance, Profile):
                ids.append(instance.id)
            if isinstance(instance, (Affiliation, EmailAddress)):
                ids.append(instance.profile.id)

        for profile_id in set(ids):
            try:
                # send message to bus indicating a profile change
                publisher.publish(ProfileEvent(id=profile_id))
            except (AttributeError, RuntimeError):
                LOGGER.exception(UpdateEventFailure('Failed to send event '
                                                    'for Profile {}'.format(profile_id)))

    return wrapper
