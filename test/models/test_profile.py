from datetime import datetime, timedelta, timezone

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


def test_it_can_get_current_affiliations():
    start_date = datetime(2017, 1, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    start_date2 = datetime(2017, 2, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=1)))

    past_end_date = datetime(2017, 2, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=1)))

    address = Address(countries.get('gb'), 'City')

    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep', starts=start_date)
    affiliation2 = Affiliation('2', address=address, organisation='Org2', department='Dep', starts=start_date2)
    affiliation3 = Affiliation('3', address=address, organisation='Org2',
                               department='Dep', starts=start_date, ends=past_end_date)

    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    # current affiliations
    profile.add_affiliation(affiliation)
    profile.add_affiliation(affiliation2)

    # past affiliation, should not be returned with current affiliations
    profile.add_affiliation(affiliation3)

    assert len(profile.get_affiliations()) == 2


def test_it_can_get_all_affiliations_including_non_current():
    start_date = datetime(2017, 1, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    start_date2 = datetime(2017, 2, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=1)))

    past_end_date = datetime(2017, 2, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=1)))

    address = Address(countries.get('gb'), 'City')

    affiliation = Affiliation('1', address=address, organisation='Org', department='Dep', starts=start_date)
    affiliation2 = Affiliation('2', address=address, organisation='Org2', department='Dep', starts=start_date2)
    affiliation3 = Affiliation('3', address=address, organisation='Org2',
                               department='Dep', starts=start_date, ends=past_end_date)

    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    # current affiliations
    profile.add_affiliation(affiliation)
    profile.add_affiliation(affiliation2)

    # past affiliation, should be returned when requesting 'all' affiliations
    profile.add_affiliation(affiliation3)

    assert len(profile.get_affiliations(current_only=False)) == 3


# TODO test that affiliations are in position based order
