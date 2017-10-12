from datetime import datetime, timedelta, timezone

from freezegun import freeze_time
from iso3166 import countries
import pendulum

from profiles.models import Address, Affiliation


def test_it_can_be_printed():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime.now())

    assert repr(affiliation) == "<Affiliation '1'>"


def test_it_has_an_id():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime.now())

    assert affiliation.id == '1'


def test_it_has_an_address():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime.now())

    assert affiliation.address == Address(countries.get('gb'), 'City')


def test_it_has_an_organisation():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime.now())

    assert affiliation.organisation == 'Organisation'


def test_it_may_have_a_department():
    has = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', datetime.now(),
                      department='Department')
    has_not = Affiliation('2', Address(countries.get('gb'), 'City'), 'Organisation', datetime.now())

    assert has.department == 'Department'
    assert has_not.department is None


@freeze_time('2017-01-01 00:00:00')
def test_it_has_a_start_date():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime.now())

    assert affiliation.starts == pendulum.timezone('utc').convert(datetime.now())


@freeze_time('2017-01-01 00:00:00', 1)
def test_it_converts_start_dates_to_utc():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime(2017, 1, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=1))))

    assert affiliation.starts.isoformat() == '2017-01-01T00:00:00+00:00'


@freeze_time('2017-01-01 00:00:00')
def test_it_may_have_an_end_date():
    has = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', datetime.now(),
                      ends=datetime.now())
    has_not = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', datetime.now())

    assert has.ends == pendulum.timezone('utc').convert(datetime.now())
    assert has_not.ends is None


@freeze_time('2017-01-01 00:00:00', 1)
def test_it_converts_end_dates_to_utc():
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation',
                              datetime.now(),
                              ends=datetime(2017, 1, 1, 1, 0, 0,
                                            tzinfo=timezone(timedelta(hours=1))))

    assert affiliation.ends.isoformat() == '2017-01-01T00:00:00+00:00'


def test_it_may_be_restricted():
    has = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', datetime.now(),
                      restricted=True)
    has_not = Affiliation('2', Address(countries.get('gb'), 'City'), 'Organisation', datetime.now())

    assert has.restricted is True
    assert has_not.restricted is False
