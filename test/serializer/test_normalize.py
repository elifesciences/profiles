from datetime import datetime

from iso3166 import countries

from profiles.models import Address, Affiliation, Name, Profile
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
        'affiliations': [],
        'orcid': '0000-0002-1825-0097'
    }


def test_it_normalizes_profile_with_an_affiliation():
    address = Address(countries.get('gb'), 'City', 'Region')
    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep', starts=datetime.now())
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))

    profile.add_affiliation(affiliation)

    assert normalize(profile) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
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
        ]
    }


# def test_it_normalizes_profile_with_affiliations():
#     address = Address(countries.get('gb'), 'City', 'Region')
#     address2 = Address(countries.get('gb'), 'City2', 'Region2')
#     affiliation = Affiliation('1', address=address, organisation='Org', department='Dep', starts=datetime.now())
#     affiliation2 = Affiliation('2', address=address2, organisation='Org2', department='Dep', starts=datetime.now())
#
#     profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))
#
#     profile.add_affiliation(affiliation)
#     profile.add_affiliation(affiliation2)
#
#
#     assert normalize(profile) == {
#         'id': '12345678',
#         'name': {
#             'preferred': 'Foo Bar',
#             'index': 'Bar, Foo',
#         },
#         'affiliations': [
#             {
#                 "name": [
#                     "Dep",
#                     "Org"
#                 ],
#                 "address": {
#                     "formatted": [
#                         "City",
#                         "Region",
#                         "GB"
#                     ],
#                     "components": {
#                         "locality": [
#                             "City"
#                         ],
#                         "area": [
#                             "Region"
#                         ],
#                         "country": "United Kingdom of Great Britain and Northern Ireland"
#                     }
#                 }
#             },
#             {
#                 "name": [
#                     "Dep",
#                     "Org2"
#                 ],
#                 "address": {
#                     "formatted": [
#                         "City2",
#                         "Region2",
#                         "GB"
#                     ],
#                     "components": {
#                         "locality": [
#                             "City2"
#                         ],
#                         "area": [
#                             "Region2"
#                         ],
#                         "country": "United Kingdom of Great Britain and Northern Ireland"
#                     }
#                 }
#             }
#         ]
#     }

# TODO test that only have current affiliations
# TODO test that affiliations are in the position based order

# TODO test it include email addresses
