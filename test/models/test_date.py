from datetime import datetime

from freezegun import freeze_time
import pytest

from profiles.models import Date


def test_it_can_be_printed():
    date1 = Date(2017)
    date2 = Date(2017, 1)
    date3 = Date(2017, 1, 2)

    assert repr(date1) == "<Date '2017'>"
    assert repr(date2) == "<Date '2017-01'>"
    assert repr(date3) == "<Date '2017-01-02'>"


def test_it_casts_to_a_string():
    date1 = Date(2017)
    date2 = Date(2017, 1)
    date3 = Date(2017, 1, 2)

    assert str(date1) == '2017'
    assert str(date2) == '2017-01'
    assert str(date3) == '2017-01-02'


@freeze_time('2017-01-02 00:00:00')
def test_it_can_be_created_from_a_datetime():
    date = Date.from_datetime(datetime.now())

    assert date == Date(2017, 1, 2)


@freeze_time('2017-01-02 00:00:00')
def test_it_can_be_created_for_yesterday():
    date = Date.yesterday()

    assert date == Date(2017, 1, 1)


@freeze_time('2017-01-02 00:00:00')
def test_it_can_be_created_for_today():
    date = Date.today()

    assert date == Date(2017, 1, 2)


@freeze_time('2017-01-02 00:00:00')
def test_it_can_be_created_for_tomorrow():
    date = Date.tomorrow()

    assert date == Date(2017, 1, 3)


def test_it_has_a_year():
    date = Date(2017)

    assert date.year == 2017


def test_it_may_have_a_month():
    has = Date(2017, 1)
    has_not = Date(2017)

    assert has.month == 1
    assert has_not.month is None


def test_it_must_have_a_valid_month():
    with pytest.raises(ValueError):
        Date(2017, 0)
    with pytest.raises(ValueError):
        Date(2017, 13)


def test_it_may_have_a_day():
    has = Date(2016, 2, 29)
    has_not = Date(2017, 1)

    assert has.day == 29
    assert has_not.day is None


def test_it_must_have_a_month_to_have_a_day():
    with pytest.raises(ValueError):
        Date(2017, None, 2)


def test_it_must_be_a_valid_date():
    with pytest.raises(ValueError):
        Date(2017, 0, 0)
    with pytest.raises(ValueError):
        Date(2017, 13, 31)
    with pytest.raises(ValueError):
        Date(2017, 12, 32)
    with pytest.raises(ValueError):
        Date(2017, 2, 29)


def test_it_can_become_the_lowest_possible_datetime():
    date1 = Date(2017)
    date2 = Date(2017, 2)
    date3 = Date(2017, 3, 4)

    assert date1.lowest_possible().isoformat() == '2017-01-01T00:00:00'
    assert date2.lowest_possible().isoformat() == '2017-02-01T00:00:00'
    assert date3.lowest_possible().isoformat() == '2017-03-04T00:00:00'


def test_it_can_become_the_highest_possible_datetime():
    date1 = Date(2017)
    date2 = Date(2017, 2)
    date3 = Date(2016, 2)
    date4 = Date(2017, 3, 4)

    assert date1.highest_possible().isoformat() == '2017-12-31T00:00:00'
    assert date2.highest_possible().isoformat() == '2017-02-28T00:00:00'
    assert date3.highest_possible().isoformat() == '2016-02-29T00:00:00'
    assert date4.highest_possible().isoformat() == '2017-03-04T00:00:00'


def test_it_can_be_compared():
    date1 = Date(2017)
    date2 = Date(2017)
    date3 = Date(2017, 1)
    date4 = Date(2017, 1)
    date5 = Date(2017, 1, 2)
    date6 = Date(2017, 1, 2)

    assert date1 == date2
    assert date1 != date3
    assert date3 == date4
    assert date3 != date1
    assert date5 == date6
    assert date5 != date1
