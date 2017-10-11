from profiles.models import Name, Profile
from profiles.serializer.normalizer import normalize_snippet


def test_it_normalizes_scalars():
    assert normalize_snippet('foo') == 'foo'
    assert normalize_snippet(1) == '1'


def test_it_normalizes_profile_snippets():
    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'))

    assert dict(normalize_snippet(profile)) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
    }

    profile = Profile('12345678', Name('Foo Bar', 'Bar, Foo'), '0000-0002-1825-0097')

    assert dict(normalize_snippet(profile)) == {
        'id': '12345678',
        'name': {
            'preferred': 'Foo Bar',
            'index': 'Bar, Foo',
        },
        'orcid': '0000-0002-1825-0097',
    }
