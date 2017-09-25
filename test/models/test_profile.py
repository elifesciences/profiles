from profiles.models import Name, Profile


def test_it_can_be_printed():
    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    assert repr(profile) == "<Profile '12345678'>"


def test_it_has_an_id():
    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    assert profile.id == '12345678'


def test_it_has_a_name():
    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    assert profile.name == Name('foo')


def test_it_has_an_orcid():
    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    assert profile.orcid == '0000-0002-1825-0097'
