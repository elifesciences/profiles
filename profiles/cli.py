import logging
from typing import Dict
from flask import url_for
from itsdangerous import URLSafeSerializer
from profiles.exceptions import ProfileNotFound
from profiles.models import Name, Profile
from profiles.orcid import OrcidClient
from profiles.repositories import Profiles
from profiles.types import CanBeCleared

LOGGER = logging.getLogger(__name__)

def ReadConfiguration(config, method) -> None:
    "Allows calling a method on the Config object to print its result"
    if method:
        fn = getattr(config, method)
        print(fn())
    else:
        print("Error: Please provide a valid --method to call")
            
def ClearCommand(*repositories: CanBeCleared) -> None:
    [repo.clear() for repo in repositories]

def CreateProfileCommand(profiles: Profiles, name, email) -> None:
    """Allow manual creation of profiles from the commandline.

    Example:

    $ python manage.py create-profile --name "Test User" --email "test@test.com"

    """
    if name and email:
        try:
            profile = profiles.get_by_email_address(email)
        except ProfileNotFound:
            profile = Profile(profiles.next_id(), Name(name))
            profile.add_email_address(email=email, restricted=True)
            profile = profiles.add(profile)
        return profile.id, email
    else:
        print('Error: Please provide valid strings for both `--name` and `--email`')

def SetOrcidWebhooksCommand(profiles: Profiles, orcid: Dict[str, str], orcid_client: OrcidClient,
                            uri_signer: URLSafeSerializer) -> None:
    access_token = orcid.get('webhook_access_token')
    profiles = profiles.list()
    total = len(profiles)
    for index, profile in enumerate(profiles):
        LOGGER.debug('%s of %s: %s', index + 1, total, profile)
        uri = url_for('webhook._update', payload=uri_signer.dumps(profile.orcid),
                      _external=True)
        orcid_client.set_webhook(profile.orcid, uri, access_token)
