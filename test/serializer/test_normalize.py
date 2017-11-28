from hypothesis import given
from hypothesis.extra.fakefactory import fake_factory
from hypothesis.strategies import booleans, integers, text
from iso3166 import countries

from profiles.models import Address, Affiliation, EmailAddress, Name, Profile
from profiles.serializer.normalizer import normalize


@given(text(), integers())
def test_it_normalizes_scalars(string, num):
    assert normalize(string) == string
    assert normalize(num) == num


@given(text(), text(), text())
def test_it_normalizes_profiles(id_, preferred, index):
    profile = Profile(id_, Name(preferred, index))

    assert normalize(profile) == {
        'id': id_,
        'name': {
            'preferred': preferred,
            'index': index
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


@given(text(), text(), text(), text(), fake_factory('email'), booleans())
def test_it_normalizes_profile_with_single_email_address(id_, preferred, index, orcid, email,
                                                         restricted):
    profile = Profile(id_, Name(preferred, index), orcid)
    profile.add_email_address(email, restricted=restricted)

    normalized_profile = normalize(profile)

    assert normalized_profile['emailAddresses'] == [
        {
            'access': 'restricted' if restricted else 'public',
            'value': email,
        }
    ]


@given(text(), text(), text(), text(), fake_factory('email'))
def test_it_normalizes_profile_with_multiple_email_addresses(id_, preferred, index, orcid, email):
    profile = Profile(id_, Name(preferred, index), orcid)
    profile.add_email_address(email)
    profile.add_email_address('2' + email)

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
    assert normalized_profile['emailAddresses'][0]['value'] == primary_address


def test_it_normalizes_profile_with_an_affiliation(yesterday):
    address = Address(countries.get('gb'), 'City', 'Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=yesterday)
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
                'access': 'public',
                'value': {
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
                },
            }
        ]
    }


def test_it_normalizes_profile_with_affiliations(yesterday):
    address = Address(countries.get('gb'), 'City', 'Region')
    address2 = Address(countries.get('gb'), 'City2', 'Region2')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=yesterday)
    affiliation2 = Affiliation('2', address=address2, organisation='Org2', department='Dep',
                               starts=yesterday, restricted=True)

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
                'access': 'restricted',
                'value': {
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
            },
            {
                'access': 'public',
                'value': {
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
                },
            }
        ]
    }


def test_it_normalizes_affiliation(yesterday):
    address = Address(countries.get('gb'), 'City', 'Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep',
                              starts=yesterday)

    assert normalize(affiliation) == {
        'access': 'public',
        'value': {
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
        },
    }


@given(fake_factory('email'))
def test_it_normalizes_email_address(email):
    email_address = EmailAddress(email)

    assert normalize(email_address) == {
        'access': 'public',
        'value': email,
    }
