from typing import Dict
from unittest.mock import MagicMock, patch

from flask_sqlalchemy import models_committed
from sqlalchemy.orm import scoped_session

from profiles.events import maintain_orcid_webhook
from profiles.models import OrcidToken, Profile


def test_it_sets_a_webhook_when_a_profile_is_inserted(profile: Profile,
                                                      orcid_config: Dict[str, str],
                                                      mock_orcid_client: MagicMock,
                                                      session: scoped_session):
    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client)
    models_committed.connect(receiver=webhook_maintainer)

    session.add(profile)

    with patch('profiles.orcid.request'):
        session.commit()

    assert mock_orcid_client.set_webhook.call_count == 1
    assert mock_orcid_client.set_webhook.call_args[0][0] == '0001-0002-1825-0097'
    assert mock_orcid_client.set_webhook.call_args[0][1] == 'http://localhost/orcid-webhook/' \
                                                            '0001-0002-1825-0097'


def test_it_sets_a_webhook_when_a_profile_is_updated(profile: Profile,
                                                     orcid_config: Dict[str, str],
                                                     mock_orcid_client: MagicMock,
                                                     session: scoped_session):
    session.add(profile)
    with patch('profiles.orcid.request'):
        session.commit()

    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client)
    models_committed.connect(receiver=webhook_maintainer)

    profile.add_email_address('1@example.com')
    session.add(profile)
    with patch('profiles.orcid.request'):
        session.commit()

    assert mock_orcid_client.set_webhook.call_count == 1
    assert mock_orcid_client.set_webhook.call_args[0][0] == '0001-0002-1825-0097'
    assert mock_orcid_client.set_webhook.call_args[0][1] == 'http://localhost/orcid-webhook/' \
                                                            '0001-0002-1825-0097'


def test_it_will_remove_the_webhook_when_a_profile_is_deleted(profile: Profile,
                                                              orcid_config: Dict[str, str],
                                                              mock_orcid_client: MagicMock,
                                                              session: scoped_session):
    session.add(profile)
    with patch('profiles.orcid.request'):
        session.commit()

    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client)
    models_committed.connect(receiver=webhook_maintainer)

    session.delete(profile)
    with patch('profiles.orcid.request'):
        session.commit()

    assert mock_orcid_client.remove_webhook.call_count == 1


def test_it_ignores_other_models_being_committed(orcid_token: OrcidToken,
                                                 orcid_config: Dict[str, str],
                                                 mock_orcid_client: MagicMock,
                                                 session: scoped_session):
    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client)
    models_committed.connect(receiver=webhook_maintainer)

    session.add(orcid_token)
    session.commit()

    assert mock_orcid_client.set_webhook.call_count == 0
    assert mock_orcid_client.remove_webhook.call_count == 0


def test_it_has_a_valid_signal_handler_registered_on_app():
    registered_handler_names = [recv.__name__ for id_, recv in models_committed.receivers.items()]
    assert 'webhook_maintainer' in registered_handler_names
