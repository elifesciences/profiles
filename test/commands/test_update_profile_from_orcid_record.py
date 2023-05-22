from unittest import mock
from hypothesis import given
from hypothesis.searchstrategy import SearchStrategy
from hypothesis.strategies import sampled_from
from iso3166 import countries
import pytest

from profiles.commands import extract_email_addresses, update_profile_from_orcid_record
from profiles.models import Address, Affiliation, Date, Name, Profile


def given_names() -> SearchStrategy:
    return sampled_from(['Francisco', 'Verónica', 'Татьяна', '璞玉', 'Francisco Javier', 'jian',
                         'MARIA ISABEL'])


def family_name() -> SearchStrategy:
    return sampled_from(['Baños', 'López López', 'Яковлева', '田', 'Cuevas-de-la-Rosa', 'yilang',
                         'GONZALEZ SANCHEZ'])


def test_it_extracts_email_addresses():
    orcid_record = {'person': {
        'emails': {'email': [
            {'email': '1@example.com', 'primary': False, 'verified': True, 'visibility': 'LIMIT'},
            {'email': '2@example.com', 'primary': True, 'verified': True, 'visibility': 'PUBLIC'},
        ]},
    }}

    expected = [
        {'email': '1@example.com', 'primary': False, 'verified': True, 'visibility': 'LIMIT'},
        {'email': '2@example.com', 'primary': True, 'verified': True, 'visibility': 'PUBLIC'}
    ]

    assert extract_email_addresses(orcid_record) == expected


def test_it_can_extract_email_addresses_ignoring_unverified():
    orcid_record = {'person': {
        'emails': {'email': [
            {'email': '1@example.com', 'primary': False, 'verified': False, 'visibility': 'LIMIT'},
            {'email': '2@example.com', 'primary': True, 'verified': True, 'visibility': 'PUBLIC'},
        ]},
    }}

    expected_with = [
        {'email': '1@example.com', 'primary': False, 'verified': False, 'visibility': 'LIMIT'},
        {'email': '2@example.com', 'primary': True, 'verified': True, 'visibility': 'PUBLIC'}
    ]
    expected_without = [
        {'email': '2@example.com', 'primary': True, 'verified': True, 'visibility': 'PUBLIC'}
    ]

    assert extract_email_addresses(orcid_record, only_verified=False) == expected_with
    assert extract_email_addresses(orcid_record, only_verified=True) == expected_without


@given(given_names(), family_name())
def test_it_updates_the_name(given_names: str, family_name: str):
    profile = Profile('12345678', Name('Old Name'))
    orcid_record = {'person': {
        'name': {'family-name': {'value': family_name}, 'given-names': {'value': given_names}}}
    }

    update_profile_from_orcid_record(profile, orcid_record)

    assert profile.name.preferred == '{} {}'.format(given_names, family_name)
    assert profile.name.index == '{}, {}'.format(family_name, given_names)


@pytest.mark.parametrize('name', [
    ({}),
    ({'family-name': None, 'given-names': None}),
    ({'family-name': {'value': ''}, 'given-names': {'value': ''}}),
])
def test_it_does_not_updates_the_name_if_its_missing(name):
    profile = Profile('12345678', Name('Old Name'))
    orcid_record = {'person': {'name': name}}

    update_profile_from_orcid_record(profile, orcid_record)

    assert profile.name == Name('Old Name')


@given(family_name())
def test_it_updates_the_name_if_there_is_no_given_name(family_name: str):
    profile = Profile('12345678', Name('Old Name'))
    orcid_record = {'person': {
        'name': {'family-name': {'value': family_name}}}
    }

    update_profile_from_orcid_record(profile, orcid_record)

    assert profile.name.preferred == family_name
    assert profile.name.index == family_name


@given(given_names())
def test_it_updates_the_name_if_there_is_no_family_name(given_names: str):
    profile = Profile('12345678', Name('Old Name'))
    orcid_record = {'person': {
        'name': {'given-names': {'value': given_names}}}
    }

    update_profile_from_orcid_record(profile, orcid_record)

    assert profile.name.preferred == given_names
    assert profile.name.index == given_names


def test_it_adds_affiliations():
    profile = Profile('12345678', Name('Name'))
    orcid_record = {'activities-summary': {
        'employments': {'employment-summary': [
            {'put-code': 1, 'start-date': {'year': {'value': '2016'}, 'month': {'value': '12'},
                                           'day': {'value': '31'}},
             'organization': {'name': 'Organisation 1',
                              'address': {'city': 'City 1', 'country': 'GB'}},
             'visibility': 'PUBLIC'},
            {'put-code': 2, 'start-date': {'year': {'value': '2015'}, 'month': {'value': '12'},
                                           'day': {'value': '31'}},
             'department-name': 'Department 2',
             'organization': {'name': 'Organisation 2',
                              'address': {'city': 'City 2', 'region': 'Region 2', 'country': 'US'}},
             'visibility': 'LIMIT'},
        ]},
    }}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.affiliations) == 2

    assert profile.affiliations[0].id == '1'
    assert profile.affiliations[0].restricted is False
    assert profile.affiliations[0].position == 0

    assert profile.affiliations[1].id == '2'
    assert profile.affiliations[1].restricted is True
    assert profile.affiliations[1].position == 1


def test_it_adds_affiliations_with_a_partial_start_dates():
    profile = Profile('12345678', Name('Name'))
    orcid_record = {'activities-summary': {
        'employments': {'employment-summary': [
            {'put-code': 1, 'start-date': {'year': {'value': '2016'}},
             'organization': {'name': 'Organisation 1',
                              'address': {'city': 'City 1', 'country': 'GB'}},
             'visibility': 'PUBLIC'},
            {'put-code': 2, 'start-date': {'year': {'value': '2015'}, 'month': {'value': '12'}},
             'department-name': 'Department 2',
             'organization': {'name': 'Organisation 2',
                              'address': {'city': 'City 2', 'region': 'Region 2', 'country': 'US'}},
             'visibility': 'LIMIT'},
            {'put-code': 3, 'start-date': None,
             'organization': {'name': 'Organisation 2',
                              'address': {'city': 'City 2', 'region': 'Region 2', 'country': 'US'}},
             'visibility': 'LIMIT'},
        ]},
    }}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.affiliations) == 3

    assert profile.affiliations[0].id == '1'
    assert profile.affiliations[0].restricted is False
    assert profile.affiliations[0].position == 0
    assert profile.affiliations[0].starts == Date(2016)

    assert profile.affiliations[1].id == '2'
    assert profile.affiliations[1].restricted is True
    assert profile.affiliations[1].position == 1
    assert profile.affiliations[1].starts == Date(2015, 12)

    assert profile.affiliations[2].id == '3'
    assert profile.affiliations[2].restricted is True
    assert profile.affiliations[2].position == 2
    assert profile.affiliations[2].starts is None


def test_it_adds_affiliations_with_a_partial_end_dates():
    profile = Profile('12345678', Name('Name'))
    orcid_record = {'activities-summary': {
        'employments': {'employment-summary': [
            {'put-code': 1, 'start-date': {'year': {'value': '2015'}, 'month': {'value': '1'},
                                           'day': {'value': '1'}},
             'end-date': {'year': {'value': '2016'}},
             'organization': {'name': 'Organisation 1',
                              'address': {'city': 'City 1', 'country': 'GB'}},
             'visibility': 'PUBLIC'},
            {'put-code': 2, 'start-date': {'year': {'value': '2015'}, 'month': {'value': '1'},
                                           'day': {'value': '1'}},
             'end-date': {'year': {'value': '2017'}, 'month': {'value': '12'}},
             'department-name': 'Department 2',
             'organization': {'name': 'Organisation 2',
                              'address': {'city': 'City 2', 'region': 'Region 2', 'country': 'US'}},
             'visibility': 'LIMIT'},
        ]},
    }}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.affiliations) == 2

    assert profile.affiliations[0].id == '1'
    assert profile.affiliations[0].restricted is False
    assert profile.affiliations[0].position == 0
    assert profile.affiliations[0].ends == Date(2016)

    assert profile.affiliations[1].id == '2'
    assert profile.affiliations[1].restricted is True
    assert profile.affiliations[1].position == 1
    assert profile.affiliations[1].ends == Date(2017, 12)


def test_it_removes_affiliations():
    profile = Profile('12345678', Name('Name'))
    profile.add_affiliation(
        Affiliation('1', Address(countries.get('gb'), 'City 1'), 'Organisation 1', Date(2017)))
    orcid_record = {}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.affiliations) == 0


def test_it_updates_affiliations_2(database, session):
    """somehow `profiles` is achieving this state here:
    - https://github.com/elifesciences/issues/issues/8275"""

    # extant profile
    profile = Profile('12345678', Name('Name'))
    session.add(profile)
    session.commit()

    # request comes in to update some affiliations
    # we simulate that here without committing the session/transaction
    address = Address(countries.get('gb'), 'City 1')
    aff1 = Affiliation('1', address, 'Organisation 1', Date(2017))
    profile.add_affiliation(aff1)

    def killerfn(*args):
        # meanwhile, another request has come along to also update that profile with the same affiliation.
        # one of the two requests will succeed.
        # we can't (easily) simulate multiple threads here and whatever state the database session is in,
        # so we skip the logic in `profile.add_affiliation` and just add it directly.
        aff2 = Affiliation('1', address, 'Organisation 1', Date(2017))
        aff2.profile = profile
        session.add(aff2)

    with mock.patch("profiles.commands._update_affiliations_from_orcid_record", side_effect=killerfn):
        # request comes along from orcid to update profile with a new affliation
        orcid_record = {
            'person': {
                'emails': {
                    'email': [
                        {'email': '1@example.com', 'primary': False, 'verified': True, 'visibility': 'LIMIT'},
                    ]
                }
            },
        }

        # ensure logger.exception is capturing the incoming record
        from sqlalchemy import exc
        with pytest.raises(exc.IntegrityError):
            with mock.patch("profiles.commands.LOGGER.exception") as log:
                update_profile_from_orcid_record(profile, orcid_record)
        assert log.call_count == 1
        assert log.call_args[1]['extra']['orcid_record'] == orcid_record

def test_it_adds_email_addresses():
    profile = Profile('12345678', Name('Name'))
    orcid_record = {'person': {
        'emails': {'email': [
            {'email': '1@example.com', 'primary': False, 'verified': True, 'visibility': 'LIMIT'},
            {'email': '2@example.com', 'primary': True, 'verified': True, 'visibility': 'PUBLIC'},
        ]},
    }}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.email_addresses) == 2

    assert profile.email_addresses[0].email == '2@example.com'
    assert profile.email_addresses[0].restricted is False
    assert profile.email_addresses[0].position == 0

    assert profile.email_addresses[1].email == '1@example.com'
    assert profile.email_addresses[1].restricted is True
    assert profile.email_addresses[1].position == 1


def test_it_ignores_unverified_email_addresses():
    profile = Profile('12345678', Name('Name'))
    orcid_record = {'person': {
        'emails': {'email': [
            {'email': '1@example.com', 'primary': True, 'verified': False, 'visibility': 'PUBLIC'},
        ]},
    }}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.email_addresses) == 0


def test_it_removes_email_addresses():
    profile = Profile('12345678', Name('Name'))
    profile.add_email_address('1@example.com')

    orcid_record = {'person': {}}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.email_addresses) == 0


def test_it_updates_email_addresses():
    profile = Profile('12345678', Name('Name'))
    profile.add_email_address('1@example.com', True, True)

    orcid_record = {'person': {
        'emails': {'email': [
            {'email': '1@example.com', 'primary': True, 'verified': True, 'visibility': 'PUBLIC'},
        ]},
    }}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.email_addresses) == 1

    assert profile.email_addresses[0].email == '1@example.com'
    assert profile.email_addresses[0].restricted is False
    assert profile.email_addresses[0].position == 0
