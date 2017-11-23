import logging
from typing import Callable

from elife_bus_sdk.events import ProfileEvent
from elife_bus_sdk.publishers import EventPublisher
from flask import Flask

from profiles.exceptions import UpdateEventFailure
from profiles.models import Affiliation, EmailAddress, Profile


LOGGER = logging.getLogger(__name__)


def send_update_events(publisher: EventPublisher) -> Callable[..., None]:
    def event_handler(sender: Flask, changes: tuple) -> None:  # pylint:disable=unused-argument
        ids = []

        LOGGER.info('Processing event(s)')

        for instance, operation in changes:  # pylint:disable=unused-variable
            LOGGER.info('Event: %s - %s', instance, operation)
            if isinstance(instance, Profile):
                ids.append(instance.id)
            if isinstance(instance, (Affiliation, EmailAddress)):
                ids.append(instance.profile.id)

        for profile_id in set(ids):
            try:
                LOGGER.info('Sending event for profile id: %s', profile_id)

                # send message to bus indicating a profile change
                publisher.publish(ProfileEvent(id=profile_id))

                LOGGER.info('Event sent for profile id: %s', profile_id)
            except (AttributeError, RuntimeError):
                LOGGER.exception(UpdateEventFailure('Failed to send event '
                                                    'for Profile {}'.format(profile_id)))

    return event_handler