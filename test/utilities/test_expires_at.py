from datetime import datetime, timezone

from freezegun import freeze_time

from profiles.utilities import expires_at


@freeze_time('2017-01-01 00:00:00')
def test_it_adds_time():
    output = expires_at(1234)

    assert datetime(2017, 1, 1, 0, 20, 34, tzinfo=timezone.utc).isoformat() == output.isoformat()


@freeze_time('2017-01-01 00:00:00', 1)
def test_it_adds_time_relative_to_utc():
    output = expires_at(1234)

    assert datetime(2017, 1, 1, 0, 20, 34, tzinfo=timezone.utc).isoformat() == output.isoformat()
