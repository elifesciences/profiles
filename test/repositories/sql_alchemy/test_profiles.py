import pytest

from profiles.database import db
from profiles.exceptions import ProfileNotFound
from profiles.models import Name, Profile
from profiles.repositories import SQLAlchemyProfiles


def test_it_contains_profiles():
    profiles = SQLAlchemyProfiles(db)

    profile1 = Profile('12345678', Name('name1'), '0000-0002-1825-0097')
    profile2 = Profile('12345679', Name('name2'))

    profile1 = profiles.add(profile1)
    profile2 = profiles.add(profile2)

    assert profiles.get('12345678') == profile1
    assert profiles.get('12345679') == profile2

    with pytest.raises(ProfileNotFound):
        profiles.get('12345670')


def test_it_avoids_orcid_conflicts():
    profiles = SQLAlchemyProfiles(db)

    profile1 = Profile('12345678', Name('name1'), '0000-0002-1825-0097')
    profile2 = Profile('12345679', Name('name2'), '0000-0002-1825-0097')

    profile1 = profiles.add(profile1)
    profile2 = profiles.add(profile2)

    assert profile1 == profile2

    with pytest.raises(ProfileNotFound):
        profiles.get('12345679')


def test_it_avoids_email_address_conflicts():
    profiles = SQLAlchemyProfiles(db)

    profile1 = Profile('12345678', Name('name1'))
    profile1.add_email_address('foo@example.com')
    profile2 = Profile('12345679', Name('name2'))
    profile2.add_email_address('foo@example.com')

    profile1 = profiles.add(profile1)
    profile2 = profiles.add(profile2)

    assert profile1 == profile2

    with pytest.raises(ProfileNotFound):
        profiles.get('12345679')


def test_it_gets_profiles_by_their_orcid():
    profiles = SQLAlchemyProfiles(db)

    profile1 = Profile('12345678', Name('name1'), '0000-0002-1825-0097')
    profile2 = Profile('12345679', Name('name2'))

    profiles.add(profile1)
    profiles.add(profile2)

    assert profiles.get_by_orcid('0000-0002-1825-0097') == profile1

    with pytest.raises(ProfileNotFound):
        profiles.get_by_orcid('0000-0002-1825-0098')


def test_it_gets_profiles_by_their_email_address():
    profiles = SQLAlchemyProfiles(db)

    profile1 = Profile('12345678', Name('name1'))
    profile1.add_email_address('foo@example.com')
    profile1.add_email_address('bar@example.com')
    profile2 = Profile('12345679', Name('name2'))
    profile2.add_email_address('baz@example.com')

    profiles.add(profile1)
    profiles.add(profile2)

    assert profiles.get_by_email_address('foo@example.com') == profile1
    assert profiles.get_by_email_address('bar@example.com') == profile1
    assert profiles.get_by_email_address('foo@example.com', 'bar@example.com') == profile1
    assert profiles.get_by_email_address('foobar@example.com', 'bar@example.com') == profile1
    assert profiles.get_by_email_address('baz@example.com') == profile2

    with pytest.raises(ProfileNotFound):
        profiles.get_by_email_address()
    with pytest.raises(ProfileNotFound):
        profiles.get_by_email_address('qux@example.com')
    with pytest.raises(ProfileNotFound):
        profiles.get_by_email_address('qux@example.com', 'quxx@example.com')


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

    profiles.add(Profile('11111111', Name('name')))

    assert profiles.next_id() == '11111112'


def test_it_limits_retrying_when_generating_the_next_profile_id():
    def id_generator():
        return '11111111'

    profiles = SQLAlchemyProfiles(db, id_generator)

    profiles.add(Profile('11111111', Name('name')))

    with pytest.raises(RuntimeError):
        assert profiles.next_id()


def test_it_lists_profiles():
    profiles = SQLAlchemyProfiles(db)
    profiles.add(Profile('11111111', Name('Name 1')))
    profiles.add(Profile('11111112', Name('Name 2')))
    profiles.add(Profile('11111113', Name('Name 3')))

    profiles_list = profiles.list()

    assert len(profiles_list) == 3
    assert str(profiles_list[0].name) == 'Name 3'
    assert str(profiles_list[1].name) == 'Name 2'
    assert str(profiles_list[2].name) == 'Name 1'

    profiles_list = profiles.list(desc=False)

    assert len(profiles_list) == 3
    assert str(profiles_list[0].name) == 'Name 1'
    assert str(profiles_list[1].name) == 'Name 2'
    assert str(profiles_list[2].name) == 'Name 3'


def test_it_lists_profiles_in_slices():
    profiles = SQLAlchemyProfiles(db)
    profiles.add(Profile('11111111', Name('Name 1')))
    profiles.add(Profile('11111112', Name('Name 2')))
    profiles.add(Profile('11111113', Name('Name 3')))

    profiles_list = profiles.list(limit=1)

    assert len(profiles_list) == 1
    assert str(profiles_list[0].name) == 'Name 3'

    profiles_list = profiles.list(offset=1)

    assert len(profiles_list) == 2
    assert str(profiles_list[0].name) == 'Name 2'
    assert str(profiles_list[1].name) == 'Name 1'

    profiles_list = profiles.list(limit=1, offset=1)

    assert len(profiles_list) == 1
    assert str(profiles_list[0].name) == 'Name 2'

    profiles_list = profiles.list(offset=10)

    assert len(profiles_list) == 0


def test_it_clears_profiles():
    profiles = SQLAlchemyProfiles(db)
    profiles.add(Profile('11111111', Name('name')))
    profiles.clear()

    with pytest.raises(ProfileNotFound):
        profiles.get('11111111')
