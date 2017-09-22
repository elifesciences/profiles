from unittest.mock import MagicMock, patch

import pytest

from profiles.database import db
from profiles.exceptions import ProfileNotFound
from profiles.models import Profile
from profiles.repositories import SQLAlchemyProfiles


def test_it_contains_profiles():
    profiles = SQLAlchemyProfiles(db)

    profile1 = Profile('12345678', 'name1', '0000-0002-1825-0097')
    profile2 = Profile('12345679', 'name2')

    profiles.add(profile1)
    profiles.add(profile2)

    assert profiles.get('12345678') == profile1
    assert profiles.get('12345679') == profile2

    with pytest.raises(ProfileNotFound):
        profiles.get('12345670')


def test_it_gets_profiles_by_their_orcid():
    profiles = SQLAlchemyProfiles(db)

    profile1 = Profile('12345678', 'name1', '0000-0002-1825-0097')
    profile2 = Profile('12345679', 'name2')

    profiles.add(profile1)
    profiles.add(profile2)

    assert profiles.get_by_orcid('0000-0002-1825-0097') == profile1

    with pytest.raises(ProfileNotFound):
        profiles.get_by_orcid('0000-0002-1825-0098')


@patch('profiles.repositories.generate_random_string')
def test_it_generates_the_next_profile_id(generate_random_string: MagicMock):
    profiles = SQLAlchemyProfiles(db)

    generate_random_string.return_value = '11111111'

    assert profiles.next_id() == '11111111'


@patch('profiles.repositories.generate_random_string')
def test_it_retries_generating_the_next_profile_id(generate_random_string: MagicMock):
    profiles = SQLAlchemyProfiles(db)

    profiles.add(Profile('11111111', 'name'))

    generate_random_string.side_effect = ['11111111', '11111112']

    assert profiles.next_id() == '11111112'


@patch('profiles.repositories.generate_random_string')
def test_it_limits_retrying_when_generating_the_next_profile_id(generate_random_string: MagicMock):
    profiles = SQLAlchemyProfiles(db)

    profiles.add(Profile('11111111', 'name'))

    generate_random_string.side_effect = ['11111111'] * 10

    with pytest.raises(RuntimeError):
        assert profiles.next_id()
