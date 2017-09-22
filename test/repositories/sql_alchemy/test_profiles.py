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


def test_it_generates_the_next_profile_id():
    def id_generator():
        return '11111111'

    profiles = SQLAlchemyProfiles(db, id_generator)

    assert profiles.next_id() == '11111111'


def test_it_retries_generating_the_next_profile_id():
    counter = 0

    def id_generator():
        nonlocal counter
        counter = counter + 1
        return str(11111110 + counter)

    profiles = SQLAlchemyProfiles(db, id_generator)

    profiles.add(Profile('11111111', 'name'))

    assert profiles.next_id() == '11111112'


def test_it_limits_retrying_when_generating_the_next_profile_id():
    def id_generator():
        return '11111111'

    profiles = SQLAlchemyProfiles(db, id_generator)

    profiles.add(Profile('11111111', 'name'))

    with pytest.raises(RuntimeError):
        assert profiles.next_id()
