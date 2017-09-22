from profiles.models import OrcidToken
from profiles.utilities import expires_at


def test_it_can_be_printed():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    assert repr(orcid_token) == "<OrcidToken for '0000-0002-1825-0097'>"


def test_it_has_an_orcid():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    orcid_token.orcid = '0000-0002-1825-0097'


def test_it_has_an_access_token():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    orcid_token.access_token = '1/fFAGRNJru1FTz70BzhT3Zg'


def test_it_has_an_expiry_date():
    orcid_token = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))

    orcid_token.expires_at = expires_at(1234)
