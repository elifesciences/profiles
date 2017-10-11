from profiles.models import Name, Profile
from profiles.serializer.normalizer import normalize


def test_it_normalizes_scalars():
    assert normalize('foo') == 'foo'
    assert normalize(1) == '1'


def test_it_normalizes_profiles():
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))

    assert dict(normalize(profile)) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
    }

    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'), '0000-0002-1825-0097')

    assert dict(normalize(profile)) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
        'orcid': '0000-0002-1825-0097',
    }
