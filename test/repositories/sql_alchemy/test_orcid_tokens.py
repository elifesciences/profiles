from hypothesis import given
from hypothesis.strategies import integers, text
import pytest

from profiles.database import db
from profiles.exceptions import OrcidTokenNotFound
from profiles.models import OrcidToken
from profiles.repositories import SQLAlchemyOrcidTokens
from profiles.utilities import expires_at


def test_it_contains_orcid_tokens():
    orcid_tokens = SQLAlchemyOrcidTokens(db)

    orcid_token1 = OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))
    orcid_token2 = OrcidToken('0000-0002-1825-0098', '1/fFAGRNJru1FTz70BzhT3Zh', expires_at(1234))

    orcid_tokens.add(orcid_token1)
    orcid_tokens.add(orcid_token2)

    assert orcid_tokens.get('0000-0002-1825-0097') == orcid_token1
    assert orcid_tokens.get('0000-0002-1825-0098') == orcid_token2

    with pytest.raises(OrcidTokenNotFound):
        orcid_tokens.get('0000-0002-1825-0099')


@given(text(), text(), integers(max_value=999999))
def test_it_clears_orcid_tokens(orcid, token, expire):
    orcid_tokens = SQLAlchemyOrcidTokens(db)
    orcid_tokens.add(OrcidToken(orcid, token, expires_at(expire)))
    orcid_tokens.clear()

    with pytest.raises(OrcidTokenNotFound):
        orcid_tokens.get(orcid)
