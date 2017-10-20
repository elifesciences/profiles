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
    data['emailAddresses'] = [normalize(email) for email in profile.get_email_addresses()]
    data['affiliations'] = [normalize(aff) for aff in profile.get_affiliations()]

    return data


@normalize.register(Affiliation)
def normalize_affiliation(affiliation: Affiliation) -> dict:
    return {
        "name": [affiliation.department, affiliation.organisation],
        "address": {
            "formatted": [
                affiliation.address.city,
                affiliation.address.region,
                affiliation.address.country.alpha2,
            ],
            "components": {
                "locality": [affiliation.address.city],
                "area": [affiliation.address.region],
                "country": affiliation.address.country.name
            }
        }
    }


@normalize.register(EmailAddress)
def normalize_email_address(email_address: EmailAddress):
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
