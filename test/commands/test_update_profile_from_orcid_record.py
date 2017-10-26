from freezegun import freeze_time
from iso3166 import countries

from profiles.commands import update_profile_from_orcid_record
from profiles.models import Address, Affiliation, Date, Name, Profile


def test_it_updates_the_name():
    profile = Profile('12345678', Name('Old Name'))
    orcid_record = {'person': {
        'name': {'family-name': {'value': 'Family Name'}, 'given-names': {'value': 'Given Names'}}}
    }

    update_profile_from_orcid_record(profile, orcid_record)

    assert profile.name.preferred == 'Given Names Family Name'
    assert profile.name.index == 'Family Name, Given Names'


@freeze_time('2017-01-01 00:00:00')
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


@freeze_time('2017-01-01 00:00:00')
def test_it_adds_affiliations_with_a_partial_start_dates():
    profile = Profile('12345678', Name('Name'))
    orcid_record = {'activities-summary': {
        'employments': {'employment-summary': [
            {'put-code': 1, 'start-date': {'year': {'value': '2016'}},
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


def test_it_removes_affiliations():
    profile = Profile('12345678', Name('Name'))
    profile.add_affiliation(
        Affiliation('1', Address(countries.get('gb'), 'City 1'), 'Organisation 1', Date(2017)))
    orcid_record = {}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.affiliations) == 0


@freeze_time('2017-01-01 00:00:00')
def test_it_updates_affiliations():
    profile = Profile('12345678', Name('Name'))
    profile.add_affiliation(Affiliation('1', Address(countries.get('gb'), 'City 1'),
                                        'Organisation 1', Date(2017)))
    orcid_record = {'activities-summary': {
        'employments': {'employment-summary': [
            {'put-code': 1, 'department-name': 'Department 2',
             'organization': {'name': 'Organisation 2',
                              'address': {'city': 'City 2', 'region': 'Region 2', 'country': 'US'}},
             'start-date': {'year': {'value': '2016'}, 'month': {'value': '12'},
                            'day': {'value': '31'}},
             'end-date': {'year': {'value': '2018'}, 'month': {'value': '02'},
                          'day': {'value': '03'}},
             'visibility': 'LIMIT'},
        ]},
    }}

    update_profile_from_orcid_record(profile, orcid_record)

    assert len(profile.affiliations) == 1
    assert profile.affiliations[0].department == 'Department 2'
    assert profile.affiliations[0].organisation == 'Organisation 2'
    assert profile.affiliations[0].address.city == 'City 2'
    assert profile.affiliations[0].address.region == 'Region 2'
    assert profile.affiliations[0].address.country == countries.get('US')
    assert profile.affiliations[0].starts == Date(2016, 12, 31)
    assert profile.affiliations[0].ends == Date(2018, 2, 3)
    assert profile.affiliations[0].restricted is True
    assert profile.affiliations[0].position == 0


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
