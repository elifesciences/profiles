from collections import OrderedDict
from functools import singledispatch
from typing import Any

from profiles.models import Profile


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
    data = OrderedDict([
        ('id', profile.id),
        ('name', OrderedDict([
            ('preferred', profile.name),
            ('index', profile.name),
        ])),
    ])

    if profile.orcid:
        data['orcid'] = profile.orcid

    return data
