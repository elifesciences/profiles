from iso3166 import countries

from profiles.models import Affiliation


def test_it_can_be_printed():
    affiliation = Affiliation('1', countries.get('gb'), 'Organisation')

    assert repr(affiliation) == "<Affiliation '1'>"


def test_it_has_an_id():
    affiliation = Affiliation('1', countries.get('gb'), 'Organisation')

    assert affiliation.id == '1'


def test_it_has_a_country():
    affiliation = Affiliation('1', countries.get('gb'), 'Organisation')

    assert affiliation.country == countries.get('gb')


def test_it_has_an_organisation():
    affiliation = Affiliation('1', countries.get('gb'), 'Organisation')

    assert affiliation.organisation == 'Organisation'


def test_it_may_have_a_department():
    has = Affiliation('1', countries.get('gb'), 'Organisation', department='Department')
    has_not = Affiliation('2', countries.get('gb'), 'Organisation')

    assert has.department == 'Department'
    assert has_not.department is None


def test_it_may_have_a_city():
    has = Affiliation('1', countries.get('gb'), 'Organisation', city='City')
    has_not = Affiliation('2', countries.get('gb'), 'Organisation')

    assert has.city == 'City'
    assert has_not.city is None


def test_it_may_have_a_region():
    has = Affiliation('1', countries.get('gb'), 'Organisation', region='Region')
    has_not = Affiliation('2', countries.get('gb'), 'Organisation')

    assert has.region == 'Region'
    assert has_not.region is None


def test_it_may_be_restricted():
    has = Affiliation('1', countries.get('gb'), 'Organisation', restricted=True)
    has_not = Affiliation('2', countries.get('gb'), 'Organisation')

    assert has.restricted is True
    assert has_not.restricted is False
