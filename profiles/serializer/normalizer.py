from functools import singledispatch
from typing import Any

from profiles.models import Affiliation, EmailAddress, Name, Profile

ACCESS_PUBLIC = "public"
ACCESS_RESTRICTED = "restricted"


@singledispatch
def normalize(value: Any) -> Any:
    return value


@singledispatch
def normalize_restricted(value: Any) -> Any:
    return value


@singledispatch
def normalize_snippet(value: Any) -> Any:
    return value


@normalize.register(Profile)
def normalize_profile(profile: Profile) -> dict:
    data = normalize_profile_snippet(profile)
    data["emailAddresses"] = [
        normalize(email) for email in profile.get_email_addresses()
    ]
    data["affiliations"] = [normalize(aff) for aff in profile.get_affiliations()]
    return data


@normalize_restricted.register(Profile)
def normalize_restricted_profile(profile: Profile) -> dict:
    data = normalize_profile_snippet(profile)
    data["emailAddresses"] = [
        normalize(email)
        for email in profile.get_email_addresses(include_restricted=True)
    ]
    data["affiliations"] = [
        normalize(aff) for aff in profile.get_affiliations(include_restricted=True)
    ]

    return data


@normalize.register(Affiliation)
def normalize_affiliation(affiliation: Affiliation) -> dict:
    name = [affiliation.organisation]
    if affiliation.department is not None:
        name.insert(0, affiliation.department)

    components = {
        "locality": [affiliation.address.city],
        "area": [affiliation.address.region],
        "country": affiliation.address.country.name,
    }
    if affiliation.address.region is None:
        del components["area"]

    return {
        "access": ACCESS_RESTRICTED if affiliation.restricted else ACCESS_PUBLIC,
        "value": {
            "name": name,
            "address": {
                "formatted": [
                    v[0] if isinstance(v, list) else v for v in components.values()
                ],
                "components": components,
            },
        },
    }


@normalize.register(EmailAddress)
def normalize_email_address(email_address: EmailAddress):
    return {
        "access": ACCESS_RESTRICTED if email_address.restricted else ACCESS_PUBLIC,
        "value": email_address.email,
    }


@normalize_snippet.register(Profile)
def normalize_profile_snippet(profile: Profile) -> dict:
    data = {"id": profile.id, "name": normalize_name(profile.name)}

    if profile.orcid:
        data["orcid"] = profile.orcid

    return data


@normalize.register(Name)
def normalize_name(name: Name) -> dict:
    return {
        "preferred": name.preferred,
        "index": name.index,
    }
