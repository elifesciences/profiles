import time
import json
import logging
from typing import Dict
from flask import url_for
from itsdangerous import URLSafeSerializer
from profiles.exceptions import ProfileNotFound
from profiles.models import Name, Profile
from profiles.orcid import OrcidClient
from profiles.repositories import Profiles
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

def foo(profiles: Profiles, orcid: Dict[str, str], orcid_client: OrcidClient,
                            uri_signer: URLSafeSerializer) -> None:
    access_token = orcid.get('webhook_access_token')

    problem_profiles = {}

    bar = {
    "le6iu26f": "409 Client Error: Conflict for url: https://api.orcid.org/v2.1/0000-0002-2301-6721/record",
    "z0hvtc2g": "409 Client Error: Conflict for url: https://api.orcid.org/v2.1/0000-0003-3363-6702/record",
    "5cw1n9xf": "404 Client Error: Not Found for url: https://api.orcid.org/v2.1/None/record",
    "4qku68vz": "404 Client Error: Not Found for url: https://api.orcid.org/v2.1/None/record",
    "ssa5q9zp": "409 Client Error: Conflict for url: https://api.orcid.org/v2.1/0009-0008-6904-346X/record",
    "xv82wdz4": "404 Client Error: Not Found for url: https://api.orcid.org/v2.1/None/record",
    "7ba0avjv": "404 Client Error: Not Found for url: https://api.orcid.org/v2.1/None/record",
    "yc376ncs": "404 Client Error: Not Found for url: https://api.orcid.org/v2.1/None/record",
    "eux3p6tw": "404 Client Error: Not Found for url: https://api.orcid.org/v2.1/None/record",
    "8n60qsjh": "404 Client Error: Not Found for url: https://api.orcid.org/v2.1/None/record"
    }


    try:
        for profile in profiles.list():
            #time.sleep(1)
            triple = (profile.id, str(profile.name), profile.orcid)
            #print(triple)
            
            try:
                if profile.orcid is None:
                    # can't query this profile, should probably delete it.
                    problem_profiles[profile.id] = "no orcid"
                    continue
                
                if profile.id in bar:
                    orcid_client.get_record(profile.orcid, access_token)

            except requests.exceptions.HTTPError as ex:
                problem_profiles[profile.id] = str(ex)
                
                if ex.response.status_code == 409:
                    # https://github.com/ORCID/ORCID-Source/blob/main/orcid-api-web/tutorial/api_errors.md
                    # "This record was flagged as violating ORCID's Terms of Use and has been hidden from public view."
                    try:
                        print("removing webhook")
                        #orcid_client.remove_webhook(profile.orcid, access_token)
                        print(orcid_client.remove_webhook)
                    except Exception as ex1:
                        print("failed to remove webhook for orcid %s: %s" % (profile.orcid, str(ex1)))

                    try:

                        # I think we just delete the orcid??
                        
                        print("deleting profile")
                        profile.delete() # delete profile
                    except Exception as ex2:
                        print("failed to delete profile for orcid %s: %s" % (profile.orcid, str(ex2)))
                    
            except Exception as e:
                problem_profiles[profile.id] = str(e)
                print("unhandled exception processing profile: %s" % str(e))
                print("dying")
                break
                
    except KeyboardInterrupt:
        pass

    print(json.dumps(problem_profiles, indent=4))

    return None
