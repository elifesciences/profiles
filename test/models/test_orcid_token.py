from datetime import datetime, timedelta, timezone

from freezegun import freeze_time
from hypothesis import given
from hypothesis.strategies import integers, text

from profiles.models import OrcidToken
from profiles.utilities import expires_at

MAX_EXPIRE = 999999


@given(text(), text(), integers(min_value=-MAX_EXPIRE, max_value=MAX_EXPIRE))
def test_it_can_be_printed(orcid, token, expire):
    orcid_token = OrcidToken(orcid, token, expires_at(expire))

    assert repr(orcid_token) == "<OrcidToken for {!r}>".format(orcid)


@given(text(), text(), integers(min_value=-MAX_EXPIRE, max_value=MAX_EXPIRE))
def test_it_has_an_orcid(orcid, token, expire):
    orcid_token = OrcidToken(orcid, token, expires_at(expire))

    assert orcid_token.orcid == "{}".format(orcid)


@given(text(), text(), integers(min_value=-MAX_EXPIRE, max_value=MAX_EXPIRE))
def test_it_has_an_access_token(orcid, token, expire):
    orcid_token = OrcidToken(orcid, token, expires_at(expire))

    assert orcid_token.access_token == "{}".format(token)


@freeze_time("2017-01-01 00:00:00")
@given(text(), text(), integers(min_value=-MAX_EXPIRE, max_value=MAX_EXPIRE))
def test_it_has_an_expiry_date(orcid, token, expire):
    orcid_token = OrcidToken(orcid, token, expires_at(expire))

    assert orcid_token.expires_at == expires_at(expire)


@freeze_time("2017-01-01 00:00:00", 1)
@given(text(), text())
def test_it_converts_expiry_dates_to_utc(orcid, token):
    orcid_token = OrcidToken(
        orcid,
        token,
        datetime(2017, 1, 1, 1, 20, 34, tzinfo=timezone(timedelta(hours=1))),
    )

    assert orcid_token.expires_at.isoformat() == expires_at(1234).isoformat()


@freeze_time("2017-01-01 00:00:00")
@given(text(), text())
def test_it_add_utc_to_expiry_dates(orcid, token):
    orcid_token = OrcidToken(orcid, token, datetime(2017, 1, 1, 0, 20, 34))

    assert orcid_token.expires_at.isoformat() == expires_at(1234).isoformat()
