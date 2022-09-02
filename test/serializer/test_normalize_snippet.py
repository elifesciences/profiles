from hypothesis import given
from hypothesis.strategies import integers, text

from profiles.models import Name, Profile
from profiles.serializer.normalizer import normalize_snippet


@given(text(), integers())
def test_it_normalizes_scalars(string, num):
    assert normalize_snippet(string) == string
    assert normalize_snippet(num) == num


@given(text(), text(), text(), text(min_size=1))
def test_it_normalizes_profile_snippets(id_, preferred, index, orcid):
    profile = Profile(id_, Name(preferred, index))

    assert normalize_snippet(profile) == {
        "id": id_,
        "name": {"preferred": preferred, "index": index},
    }

    profile = Profile(id_, Name(preferred, index), orcid)

    assert normalize_snippet(profile) == {
        "id": id_,
        "name": {
            "preferred": preferred,
            "index": index,
        },
        "orcid": orcid,
    }
