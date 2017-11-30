from abc import ABC
from typing import Dict

from flask import url_for
from flask_script import Command as BaseCommand
from itsdangerous import URLSafeSerializer

from profiles.orcid import OrcidClient
from profiles.repositories import Profiles
from profiles.types import CanBeCleared


class Command(ABC, BaseCommand):
    def __call__(self, app=None, *args, **kwargs) -> None:
        with app.app_context():
            return self.run(*args, **kwargs)


class ClearCommand(Command):
    NAME = 'clear'

    def __init__(self, *repositories: CanBeCleared) -> None:
        super(ClearCommand, self).__init__()
        self.repositories = repositories

    # weird decoration made by the superclass that wraps this method
    # not going to lose sleep over this for now,
    # let's see whether we get more commands
    # and we keep flask_script in the long term
    # pylint: disable=method-hidden
    def run(self) -> None:
        for each in self.repositories:
            each.clear()


class SetOrcidWebhooksCommand(Command):
    NAME = 'set-orcid-webhooks'

    def __init__(self, profiles: Profiles, orcid: Dict[str, str], orcid_client: OrcidClient,
                 uri_signer: URLSafeSerializer) -> None:
        super(SetOrcidWebhooksCommand, self).__init__()
        self.profiles = profiles
        self.orcid = orcid
        self.orcid_client = orcid_client
        self.uri_signer = uri_signer

    # weird decoration made by the superclass that wraps this method
    # not going to lose sleep over this for now,
    # let's see whether we get more commands
    # and we keep flask_script in the long term
    # pylint: disable=method-hidden
    def run(self) -> None:
        access_token = self.orcid.get('webhook_access_token')

        for profile in self.profiles.list():
            uri = url_for('webhook._update', payload=self.uri_signer.dumps(profile.orcid),
                          _external=True)
            self.orcid_client.set_webhook(profile.orcid, uri, access_token)
