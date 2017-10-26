from datetime import datetime, timedelta, timezone

import pendulum
from iso3166 import countries

from profiles.models import Address, Affiliation, EmailAddress, Name, Profile, Date
from profiles.serializer.normalizer import normalize


def test_it_normalizes_scalars():
    assert normalize('foo') == 'foo'
    assert normalize(1) == '1'


def test_it_normalizes_profiles():
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))

    assert normalize(profile) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
        'emailAddresses': [],
        'affiliations': []
    }


def test_it_normalizes_profile_with_orcid():
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'), '0000-0002-1825-0097')

    assert normalize(profile) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
        'emailAddresses': [],
        'affiliations': [],
        'orcid': '0000-0002-1825-0097'
    }


def test_it_normalizes_profile_with_single_email_address():
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com')

    normalized_profile = normalize(profile)

    assert len(normalized_profile['emailAddresses']) == 1


def test_it_normalizes_profile_with_multiple_email_addresses():
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com')
    profile.add_email_address('2example.com')

    normalized_profile = normalize(profile)

    assert len(normalized_profile['emailAddresses']) == 2


def test_it_normalizes_profile_with_multiple_email_addresses_with_primary_address_first():
    primary_address = 'primary@example.com'

    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'), '0000-0002-1825-0097')
    profile.add_email_address('1@example.com')
    profile.add_email_address('2@example.com')
    profile.add_email_address(primary_address, primary=True)

    normalized_profile = normalize(profile)

    assert len(normalized_profile['emailAddresses']) == 3
    assert normalized_profile['emailAddresses'][0] == primary_address


def test_it_normalizes_profile_with_an_affiliation():
    starts = Date.from_datetime(pendulum.yesterday())
    address = Address(countries.get('gb'), 'City', 'Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=starts)
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))

    profile.add_affiliation(affiliation)

    assert normalize(profile) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
        'emailAddresses': [],
        'affiliations': [
            {
                "name": [
                    "Dep",
                    "Org"
                ],
                "address": {
                    "formatted": [
                        "City",
                        "Region",
                        "United Kingdom of Great Britain and Northern Ireland"
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
        ]
    }


def test_it_normalizes_profile_with_affiliations():
    starts = Date.from_datetime(pendulum.yesterday())
    address = Address(countries.get('gb'), 'City', 'Region')
    address2 = Address(countries.get('gb'), 'City2', 'Region2')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=starts)
    affiliation2 = Affiliation('2', address=address2, organisation='Org2', department='Dep',
                               starts=starts)

    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))

    profile.add_affiliation(affiliation)
    profile.add_affiliation(affiliation2)

    assert normalize(profile) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
        'emailAddresses': [],
        'affiliations': [
            {
                "name": ["Dep", "Org2"],
                "address": {
                    "formatted": [
                        "City2",
                        "Region2",
                        "United Kingdom of Great Britain and Northern Ireland"
                    ],
                    "components": {
                        "locality": ["City2"],
                        "area": ["Region2"],
                        "country": "United Kingdom of Great Britain and Northern Ireland"
                    }
                }
            },
            {
                "name": ["Dep", "Org"],
                "address": {
                    "formatted": [
                        "City",
                        "Region",
                        "United Kingdom of Great Britain and Northern Ireland"
                    ],
                    "components": {
                        "locality": ["City"],
                        "area": ["Region"],
                        "country": "United Kingdom of Great Britain and Northern Ireland"
                    }
                }
            }
        ]
    }


def test_it_normalizes_affiliation():
    starts = Date.from_datetime(pendulum.yesterday())
    address = Address(countries.get('gb'), 'City', 'Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=starts)

    assert normalize(affiliation) == {
        "name": [
            "Dep",
            "Org"
        ],
        "address": {
            "formatted": [
                "City",
                "Region",
                "United Kingdom of Great Britain and Northern Ireland"
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

    assert normalize(email_address) == '1@example.com'
