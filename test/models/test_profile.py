from hypothesis import given
from hypothesis.strategies import text
from iso3166 import countries
import pytest

from profiles.exceptions import AffiliationNotFound
from profiles.models import Address, Affiliation, Date, Name, Profile


@given(text(), text(), text())
def test_it_can_be_printed(id_, name, orcid):
    profile = Profile(id_, Name(name), orcid)

    assert repr(profile) == "<Profile {!r}>".format(id_)


@given(text(), text(), text())
def test_it_has_an_id(id_, name, orcid):
    profile = Profile(id_, Name(name), orcid)

    assert profile.id == '{}'.format(id_)


@given(text(), text(), text())
def test_it_has_a_name(id_, name, orcid):
    profile = Profile(id_, Name(name), orcid)

    assert profile.name == Name(name)


@given(text(), text(), text())
def test_it_has_an_orcid(id_, name, orcid):
    profile = Profile(id_, Name(name), orcid)

    assert profile.orcid == '{}'.format(orcid)


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


def test_it_can_get_current_affiliations(tomorrow, yesterday):
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


def test_it_can_get_all_affiliations_including_non_current(tomorrow, yesterday):
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


def test_it_can_get_all_non_restricted_affiliations(yesterday):
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


def test_it_can_get_all_affiliations_including_restricted(yesterday):
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
