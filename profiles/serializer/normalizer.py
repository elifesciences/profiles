from functools import singledispatch
from typing import Any

from profiles.models import Affiliation, EmailAddress, Name, Profile


@singledispatch
def normalize(value: Any) -> str:
    return str(value)


@singledispatch
def normalize_snippet(value: Any) -> str:
    return str(value)


@normalize.register(Profile)
def normalize_profile(profile: Profile) -> dict:
    data = normalize_profile_snippet(profile)
    data['emailAddresses'] = [normalize_snippet(email) for email in profile.email_addresses]
    data['affiliations'] = [normalize_snippet(aff) for aff in profile.get_affiliations()]

    return data


@normalize_snippet.register(Affiliation)
def normalize_affiliation_snippet(affiliation: Affiliation) -> dict:
    return {
        "name": affiliation.get_name_list(),
        "address": {
            "formatted": affiliation.address.get_formatted(),
            "components": affiliation.address.get_components()
        }
    }


@normalize_snippet.register(EmailAddress)
def normalize_email_address_snippet(email_address: EmailAddress):
    return email_address.email


@normalize_snippet.register(Profile)
def normalize_profile_snippet(profile: Profile) -> dict:
    data = {
        'id': profile.id,
        'name': normalize_name(profile.name)
    }

    if profile.orcid:
        data['orcid'] = profile.orcid

    return data


@normalize.register(Name)
def normalize_name(name: Name) -> dict:
    return {
        'preferred': name.preferred,
        'index': name.index,
    }
