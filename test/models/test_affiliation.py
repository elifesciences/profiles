from iso3166 import countries

from profiles.models import Address, Affiliation, Date


def test_it_can_be_printed():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    assert repr(affiliation) == "<Affiliation '1'>"


def test_it_has_an_id():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    assert affiliation.id == '1'


def test_it_has_an_address():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    assert affiliation.address == Address(countries.get('gb'), 'City')


def test_it_has_an_organisation():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    assert affiliation.organisation == 'Organisation'


def test_it_may_have_a_department():
    has = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017),
                      department='Department')
    has_not = Affiliation('2', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    assert has.department == 'Department'
    assert has_not.department is None


def test_it_has_a_start_date(yesterday):
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', yesterday)

    assert affiliation.starts == yesterday


def test_it_may_have_an_end_date(tomorrow, yesterday):
    has = Affiliation('1', Address(countries.get('gb'), 'City'),
                      'Organisation', yesterday, ends=tomorrow)
    has_not = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', yesterday)

    assert has.ends == tomorrow
    assert has_not.ends is None


def test_it_may_be_restricted():
    has = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017),
                      restricted=True)
    has_not = Affiliation('2', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    assert has.restricted is True
    assert has_not.restricted is False


def test_it_can_detect_if_current_without_start_date():
    address = Address(countries.get('gb'), 'City')
    affiliation = Affiliation('1', address=address, organisation='Org')

    assert affiliation.is_current() is True


def test_it_can_detect_if_current_without_ends_date(yesterday):
    address = Address(countries.get('gb'), 'City')
    affiliation = Affiliation('1', address=address, organisation='Org', starts=yesterday)

    assert affiliation.is_current() is True


def test_it_can_detect_if_current_with_ends_date(tomorrow, yesterday):
    address = Address(countries.get('gb'), 'City')
    affiliation = Affiliation('1', address=address, organisation='Org',
                              starts=yesterday, ends=tomorrow)

    assert affiliation.is_current() is True


def test_it_can_detect_if_not_current_with_future_starts_date_and_no_ends_date(tomorrow):
    address = Address(countries.get('gb'), 'City')
    affiliation = Affiliation('1', address=address, organisation='Org', starts=tomorrow)

    assert affiliation.is_current() is False


def test_it_can_detect_if_not_current_with_past_starts_date_and_past_ends_date(yesterday):
    address = Address(countries.get('gb'), 'City')
    affiliation = Affiliation('1', address=address, organisation='Org',
                              starts=yesterday, ends=yesterday)

    assert affiliation.is_current() is False


def test_it_can_detect_if_not_current_with_no_starts_date_and_past_ends_date(yesterday):
    address = Address(countries.get('gb'), 'City')
    affiliation = Affiliation('1', address=address, organisation='Org', ends=yesterday)

    assert affiliation.is_current() is False
