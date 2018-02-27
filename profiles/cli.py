import logging
from abc import ABC
from typing import Dict, List

from flask import url_for
from flask_script import Command as BaseCommand, Option
from itsdangerous import URLSafeSerializer

from profiles.exceptions import ProfileNotFound
from profiles.models import Name, Profile
from profiles.orcid import OrcidClient
from profiles.repositories import Profiles
from profiles.types import CanBeCleared

LOGGER = logging.getLogger(__name__)


class Command(ABC, BaseCommand):
    def __call__(self, app=None, *args, **kwargs) -> None:
        with app.app_context():
            return self.run(*args, **kwargs)

"Allows calling a method on the Config object to print its result"
class ReadConfiguration(Command):
    NAME = 'read-configuration'

    def __init__(self, config) -> None:
        super(ReadConfiguration, self).__init__()
        self.config = config

    def get_options(self) -> List[Option]:
        return [
            Option('-s', '--method', dest='method', type=str),
        ]

    # pylint: disable=method-hidden
    def run(self, method) -> None:
        if method:
            print(getattr(self.config, method)())
        else:
            print("Error: Please provide a valid --method to call")


class ClearCommand(Command):
    NAME = 'clear'

    def __init__(self, *repositories: CanBeCleared) -> None:
        super(ClearCommand, self).__init__()
        self.repositories = repositories

    # pylint: disable=method-hidden
    def run(self) -> None:
        for each in self.repositories:
            each.clear()


class CreateProfileCommand(Command):
    """Allow manual creation of profiles from the commandline.

    Example:

    $ python manage.py create-profile --name "Test User" --email "test@test.com"

    """
    NAME = 'create-profile'

    def __init__(self, profiles: Profiles):
        super(CreateProfileCommand, self).__init__()
        self.profiles = profiles

    def get_options(self) -> List[Option]:
        return [
            Option('-e', '--email', dest='email', type=str),
            Option('-n', '--name', dest='name', type=str),
        ]

    # pylint: disable=method-hidden,arguments-differ
    def run(self, name, email) -> None:
        # pylint is complaining about arguments differing from base class
        # though this is the recommended way to define the option args in the
        # run() definition...
        if name and email:
            try:
                profile = self.profiles.get_by_email_address(email)
            except ProfileNotFound:
                profile = Profile(self.profiles.next_id(), Name(name))
                self.profiles.add(profile)
                profile.add_email_address(email=email, restricted=True)

            return profile.id, email
        else:
            print('Error: Please provide valid strings for both `--name` and `--email`')


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

        profiles = self.profiles.list()

        total = len(profiles)
        for index, profile in enumerate(profiles):
            LOGGER.debug('%s of %s: %s', index + 1, total, profile)
            uri = url_for('webhook._update', payload=self.uri_signer.dumps(profile.orcid),
                          _external=True)
            self.orcid_client.set_webhook(profile.orcid, uri, access_token)
