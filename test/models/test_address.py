from iso3166 import countries

from profiles.models import Address


def test_it_can_be_printed():
    address = Address(countries.get('gb'), 'City')

    assert repr(address) == "<Address 'City' None 'GB'>"


def test_it_has_a_city():
    address = Address(countries.get('gb'), 'City')

    assert address.city == 'City'


def test_it_may_have_a_region():
    has = Address(countries.get('gb'), 'City', 'Region')
    has_not = Address(countries.get('gb'), 'City')

    assert has.region == 'Region'
    assert has_not.region is None


def test_it_has_a_country():
    address = Address(countries.get('gb'), 'City')

    assert address.country == countries.get('gb')


def test_it_can_be_compared():
    address = Address(countries.get('gb'), 'City')
    address1 = Address(countries.get('gb'), 'City')
    address2 = Address(countries.get('gb'), 'City 2')
    address3 = Address(countries.get('gb'), 'City', 'Region')

    assert address == address1
    assert address != address2
    assert address != address3
