from profiles.commands import update_profile_from_orcid_record
from profiles.models import Name, Profile


def test_it_updates_the_name():
    profile = Profile('12345678', Name('Old Name'))
    orcid_record = {'person': {
        'name': {'family-name': {'value': 'Family Name'}, 'given-names': {'value': 'Given Names'}}}
    }

    update_profile_from_orcid_record(profile, orcid_record)

    assert profile.name.preferred == 'Given Names Family Name'
    assert profile.name.index == 'Family Name, Given Names'


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
