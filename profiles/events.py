import logging
from typing import Any, Callable, Dict, List, Tuple

from elife_bus_sdk.events import ProfileEvent
from elife_bus_sdk.publishers import EventPublisher
from flask import url_for
from itsdangerous import URLSafeSerializer
from requests import RequestException

from profiles.database import db
from profiles.exceptions import UpdateEventFailure
from profiles.models import Affiliation, EmailAddress, Profile
from profiles.orcid import OrcidClient
from profiles.utilities import catch_exceptions

LOGGER = logging.getLogger(__name__)

OPERATION_DELETE = 'delete'
OPERATION_INSERT = 'insert'
OPERATION_UPDATE = 'update'


def maintain_orcid_webhook(orcid: Dict[str, str], orcid_client: OrcidClient,
                           uri_signer: URLSafeSerializer) -> Callable[..., None]:
    # pylint:disable=unused-argument
    @catch_exceptions(LOGGER)
    def webhook_maintainer(sender: Any, changes: List[Tuple[db.Model, str]]) -> None:
        profiles = [x for x in changes if isinstance(x[0], Profile) and x[0].orcid]

        if not profiles:
            return

        access_token = orcid.get('webhook_access_token')

        for profile, operation in profiles:
            uri = url_for('webhook._update', payload=uri_signer.dumps(profile.orcid),
                          _external=True)

            try:
                if operation == OPERATION_DELETE:
                    orcid_client.remove_webhook(profile.orcid, uri, access_token)
                elif operation == OPERATION_INSERT:
                    orcid_client.set_webhook(profile.orcid, uri, access_token)
                else:
                    # lsh@2022-11-22: ignore 'update' events from the ORM.
                    # orcid have complained about the number of PUT requests being made for
                    # established webhooks:
                    # - https://github.com/elifesciences/issues/issues/7933
                    #
                    # at this point in the code the token already exists as
                    # `set_webhook` isn't creating or updating `models.OrcidToken` entries,
                    # just pinging requests off to ORCID.
                    pass
            except RequestException:
                pass

    return webhook_maintainer


def send_update_events(publisher: EventPublisher) -> Callable[..., None]:
    # pylint:disable=unused-argument
    @catch_exceptions(LOGGER)
    def event_handler(sender: Any, changes: List[Tuple[db.Model, str]]) -> None:
        ids = []

        LOGGER.info('Processing event(s)')

        for instance, operation in changes:  # pylint:disable=unused-variable
            LOGGER.info('Found operation %s %s', operation, instance)
            if isinstance(instance, Profile):
                ids.append(instance.id)
            if isinstance(instance, (Affiliation, EmailAddress)):
                ids.append(instance.profile_id)

        for profile_id in set(ids):
            try:
                LOGGER.info('Sending event for Profile %s', profile_id)

                # send message to bus indicating a profile change
                publisher.publish(ProfileEvent(id=profile_id))

                LOGGER.info('Event sent for profile id: %s', profile_id)
            except (AttributeError, RuntimeError):
                LOGGER.exception(UpdateEventFailure('Failed to send event '
                                                    'for Profile {}'.format(profile_id)))

    return event_handler
