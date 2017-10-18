from datetime import datetime

from iso3166 import countries

from profiles.models import (
    Address,
    Affiliation,
    EmailAddress,
    Name,
    Profile
)
from profiles.serializer.normalizer import normalize_snippet


def test_it_normalizes_scalars():
    assert normalize_snippet('foo') == 'foo'
    assert normalize_snippet(1) == '1'


def test_it_normalizes_profile_snippets():
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))

    assert normalize_snippet(profile) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
    }

    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'), '0000-0002-1825-0097')

    assert normalize_snippet(profile) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
        'orcid': '0000-0002-1825-0097',
    }


def test_it_normalizes_affiliation_snippet():
    address = Address(countries.get('gb'), 'City', 'Region')
    affiliation = Affiliation('1', address=address, organisation='Org',
                              department='Dep', starts=datetime.now())

    assert normalize_snippet(affiliation) == {
        "name": [
            "Dep",
            "Org"
        ],
        "address": {
            "formatted": [
                "City",
                "Region",
                "GB"
            ],
            "components": {
                "locality": [
                    "City"
                ],
                "area": [
                    "Region"
                ],
                "country": "United Kingdom of Great Britain and Northern Ireland"
            }
        }
    }


def test_it_normalizes_email_address():
    email_address = EmailAddress('1@example.com')

    assert normalize_snippet(email_address) == '1@example.com'
