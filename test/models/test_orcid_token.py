from datetime import datetime, timedelta, timezone

from freezegun import freeze_time

from profiles.models import OrcidToken
from profiles.utilities import expires_at


def test_it_can_be_printed():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    assert repr(orcid_token) == "<OrcidToken for '0000-0002-1825-0097'>"


def test_it_has_an_orcid():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    assert orcid_token.orcid == '0000-0002-1825-0097'


def test_it_has_an_access_token():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    assert orcid_token.access_token == '1/fFAGRNJru1FTz70BzhT3Zg'


@freeze_time('2017-01-01 00:00:00')
def test_it_has_an_expiry_date():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    assert orcid_token.expires_at == expires_at(1234)


@freeze_time('2017-01-01 00:00:00', 1)
def test_it_converts_expiry_dates_to_utc():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg',
                             datetime(2017, 1, 1, 1, 20, 34, tzinfo=timezone(timedelta(hours=1))))

    assert orcid_token.expires_at.isoformat() == expires_at(1234).isoformat()


@freeze_time('2017-01-01 00:00:00')
def test_it_add_utc_to_expiry_dates():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg',
                             datetime(2017, 1, 1, 0, 20, 34))

    assert orcid_token.expires_at.isoformat() == expires_at(1234).isoformat()
