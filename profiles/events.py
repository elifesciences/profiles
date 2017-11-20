import json
import logging
from typing import Callable, Dict, List, Tuple

from elife_bus_sdk.events import ProfileEvent
from elife_bus_sdk.publishers import EventPublisher
from flask import Flask, url_for
import requests
from requests import RequestException

from profiles.database import db
from profiles.exceptions import UpdateEventFailure
from profiles.models import Affiliation, EmailAddress, Profile
from profiles.orcid import OrcidClient

LOGGER = logging.getLogger(__name__)

OPERATION_DELETE = 'delete'
OPERATION_INSERT = 'insert'
OPERATION_UPDATE = 'update'


def maintain_orcid_webhook(orcid: Dict[str, str], orcid_client: OrcidClient) -> Callable[..., None]:
    # pylint:disable=unused-argument
    def webhook_maintainer(sender: Flask, changes: List[Tuple[db.Model, str]]) -> None:
        profiles = [x for x in changes if isinstance(x[0], Profile) and x[0].orcid]

        if not profiles:
            return

        data = {
            'client_id': orcid['client_id'],
            'client_secret': orcid['client_secret'],
            'scope': '/webhook',
            'grant_type': 'client_credentials',
        }

        response = requests.post(url=orcid['token_uri'], data=data,
                                 headers={'Accept': 'application/json'})

        json_data = json.loads(response.text)
        access_token = json_data['access_token']

        for profile, operation in profiles:
            uri = url_for('webhook._update', orcid=profile.orcid, _external=True)

            try:
                if operation == OPERATION_DELETE:
                    orcid_client.remove_webhook(profile.orcid, uri, access_token)
                else:
                    orcid_client.set_webhook(profile.orcid, uri, access_token)
            except RequestException:
                pass

    return webhook_maintainer


def send_update_events(publisher: EventPublisher) -> Callable[..., None]:
    # pylint:disable=unused-argument
    def event_handler(sender: Flask, changes: List[Tuple[db.Model, str]]) -> None:
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

    return event_handler
