from datetime import datetime, timedelta, timezone

from iso3166 import countries
import pendulum
import pytest

from profiles.exceptions import AffiliationNotFound
from profiles.models import Address, Affiliation, Name, Profile, Date


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
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    assert len(profile.affiliations) == 0

    profile.add_affiliation(affiliation)

    assert len(profile.affiliations) == 1

    profile.remove_affiliation(affiliation.id)

    assert len(profile.affiliations) == 0

    with pytest.raises(AffiliationNotFound):
        profile.get_affiliation('1')


def test_it_can_get_current_affiliations():
    yesterday = Date.from_datetime(pendulum.yesterday())
    tomorrow = Date.from_datetime(pendulum.tomorrow())

    address = Address(countries.get('gb'), 'City')

    affiliation1 = Affiliation('1', address=address, organisation='Org', starts=yesterday)
    affiliation2 = Affiliation('2', address=address, organisation='Org', starts=yesterday,
                               ends=tomorrow)
    affiliation3 = Affiliation('3', address=address, organisation='Org', starts=tomorrow)
    affiliation4 = Affiliation('4', address=address, organisation='Org', starts=yesterday,
                               ends=yesterday)

    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    # current affiliations
    profile.add_affiliation(affiliation1)
    profile.add_affiliation(affiliation2)

    # future affiliation, should not be returned with current affiliations
    profile.add_affiliation(affiliation3)

    # past affiliation, should not be returned with current affiliations
    profile.add_affiliation(affiliation4)

    affiliations = profile.get_affiliations()

    assert len(affiliations) == 2
    assert affiliations[0] == affiliation2
    assert affiliations[1] == affiliation1


def test_it_can_get_all_affiliations_including_non_current():
    yesterday = Date.from_datetime(pendulum.yesterday())
    tomorrow = Date.from_datetime(pendulum.tomorrow())

    address = Address(countries.get('gb'), 'City')

    affiliation1 = Affiliation('1', address=address, organisation='Org', starts=yesterday)
    affiliation2 = Affiliation('2', address=address, organisation='Org', starts=yesterday,
                               ends=tomorrow)
    affiliation3 = Affiliation('3', address=address, organisation='Org', starts=tomorrow)
    affiliation4 = Affiliation('4', address=address, organisation='Org', starts=yesterday,
                               ends=yesterday)

    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    # current affiliations
    profile.add_affiliation(affiliation1)
    profile.add_affiliation(affiliation2)

    # future affiliation, should be returned when requesting 'all' affiliations
    profile.add_affiliation(affiliation3)

    # past affiliation, should be returned when requesting 'all' affiliations
    profile.add_affiliation(affiliation4)

    affiliations = profile.get_affiliations(current_only=False)

    assert len(affiliations) == 4
    assert affiliations[0] == affiliation4
    assert affiliations[1] == affiliation3
    assert affiliations[2] == affiliation2
    assert affiliations[3] == affiliation1


def test_it_can_get_only_non_restricted_email_addresses():
    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    profile.add_email_address('1@example.com', restricted=True)
    profile.add_email_address('2@example.com')
    profile.add_email_address('3@example.com')

    assert len(profile.get_email_addresses()) == 2


def test_it_can_get_all_email_addresses_including_restricted():
    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    profile.add_email_address('1@example.com', restricted=True)
    profile.add_email_address('2@example.com')
    profile.add_email_address('3@example.com')

    assert len(profile.get_email_addresses(include_restricted=True)) == 3


def test_it_can_get_all_non_restricted_affiliations():
    yesterday = Date.from_datetime(pendulum.yesterday())

    address = Address(countries.get('gb'), 'City')

    affiliation = Affiliation('1', address=address, organisation='Org', starts=yesterday)
    affiliation2 = Affiliation('2', address=address, organisation='Org', starts=yesterday,
                               restricted=True)
    affiliation3 = Affiliation('3', address=address, organisation='Org', starts=yesterday)

    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    profile.add_affiliation(affiliation, position=1)
    profile.add_affiliation(affiliation2, position=0)
    profile.add_affiliation(affiliation3, position=2)

    affiliations = profile.get_affiliations()

    assert len(affiliations) == 2


def test_it_can_get_all_affiliations_including_restricted():
    yesterday = Date.from_datetime(pendulum.yesterday())

    address = Address(countries.get('gb'), 'City')

    affiliation = Affiliation('1', address=address, organisation='Org', starts=yesterday)
    affiliation2 = Affiliation('2', address=address, organisation='Org', starts=yesterday,
                               restricted=True)
    affiliation3 = Affiliation('3', address=address, organisation='Org', starts=yesterday)

    profile = Profile('12345678', Name('foo'), '0000-0002-1825-0097')

    profile.add_affiliation(affiliation, position=1)
    profile.add_affiliation(affiliation2, position=0)
    profile.add_affiliation(affiliation3, position=2)

    affiliations = profile.get_affiliations(include_restricted=True)

    assert len(affiliations) == 3
