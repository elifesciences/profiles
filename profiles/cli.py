import time
import json
import logging
from typing import Dict
from flask import url_for
from itsdangerous import URLSafeSerializer
from profiles.exceptions import ProfileNotFound
from profiles.models import Name, Profile
from profiles.orcid import OrcidClient
from profiles.repositories import Profiles, OrcidTokens
from profiles.types import CanBeCleared
import requests.exceptions
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

def prune_blocked(profiles: Profiles, orcid_tokens: OrcidTokens, orcid_config: Dict[str, str], orcid_client: OrcidClient, uri_signer: URLSafeSerializer) -> None:
    """command fetches each known profile and purges it if the API responds with a HTTP 409.
    the API may respond with a HTTP 409 if the profile has been blocked/disabled."""
    access_token = orcid_config.get('webhook_access_token')

    problem_profiles = {}

    try:
        for profile in profiles.list():
            orcid = profile.orcid
            if orcid is None:
                continue

            LOGGER.info("checking profile: %s", orcid)

            try:
                orcid_client.get_record(orcid, access_token)

            except requests.exceptions.HTTPError as ex:
                problem_profiles[profile.id] = str(ex)
                if ex.response.status_code == 409:
                    # https://github.com/ORCID/ORCID-Source/blob/main/orcid-api-web/tutorial/api_errors.md
                    # "This record was flagged as violating ORCID's Terms of Use and has been hidden from public view."
                    try:
                        LOGGER.info("removing webhook for orcid %s", orcid)
                        orcid_client.remove_webhook(orcid, access_token)
                    except Exception as ex1:
                        LOGGER.error("failed to remove webhook for orcid %s: %s", orcid, str(ex1))

                    try:
                        LOGGER.info("removing profile for orcid %s", orcid)
                        profiles.remove(orcid)
                    except Exception as ex2:
                        LOGGER.error("failed to delete profile for orcid %s: %s", orcid, str(ex2))

                    try:
                        LOGGER.info("removing orcid token access token for orcid %s", orcid)
                        orcid_tokens.remove(orcid)
                    except Exception as ex3:
                        LOGGER.error("failed to delete orcid_token for orcid %s: %s", orcid, str(ex3))

            except Exception as e:
                problem_profiles[profile.id] = str(e)
                LOGGER.error("unhandled exception processing profile with orcid %s: %s", orcid, str(e))
                break

            time.sleep(1 / 4) # 250ms, max 4req/s when running sequentially

    except KeyboardInterrupt:
        pass

    if problem_profiles:
        print("--- ")
        print(json.dumps(problem_profiles, indent=4))

    return None
