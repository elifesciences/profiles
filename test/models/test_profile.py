from datetime import datetime

from iso3166 import countries
import pytest

from profiles.exceptions import AffiliationNotFound
from profiles.models import Address, Affiliation, Name, Profile


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


def test_it_can_have_affiliations():
    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime.now())

    assert len(profile.affiliations) == 0

    profile.add_affiliation(affiliation)

    assert len(profile.affiliations) == 1

    profile.remove_affiliation(affiliation.id)

    assert len(profile.affiliations) == 0

    with pytest.raises(AffiliationNotFound):
        profile.get_affiliation('1')
