from functools import singledispatch
from typing import Any

from profiles.models import Name, Profile


@singledispatch
def normalize(value: Any) -> str:
    return str(value)


@singledispatch
def normalize_snippet(value: Any) -> str:
    return str(value)


@normalize.register(Profile)
def normalize_profile(profile: Profile) -> dict:
    data = normalize_profile_snippet(profile)

    return data


@normalize_snippet.register(Profile)
def normalize_profile_snippet(profile: Profile) -> dict:
    data = {
        'id': profile.id,
        'name': normalize_name(profile.name),
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
