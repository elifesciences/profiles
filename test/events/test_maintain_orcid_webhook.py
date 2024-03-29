from unittest import skip
from typing import Callable, Dict, List
from unittest.mock import MagicMock

from flask_sqlalchemy import models_committed
from itsdangerous import URLSafeSerializer
from sqlalchemy.orm import scoped_session

from profiles.events import maintain_orcid_webhook
from profiles.models import OrcidToken, Profile


def test_it_has_a_valid_signal_handler_registered_on_app(registered_handler_names: List[str]):
    assert 'webhook_maintainer' in registered_handler_names


def test_it_sets_a_webhook_when_a_profile_is_inserted(profile: Profile,
                                                      orcid_config: Dict[str, str],
                                                      mock_orcid_client: MagicMock,
                                                      session: scoped_session,
                                                      url_safe_serializer: URLSafeSerializer,
                                                      commit: Callable[[], None]):
    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client,
                                                url_safe_serializer)
    models_committed.connect(receiver=webhook_maintainer)

    session.add(profile)

    commit()

    assert mock_orcid_client.set_webhook.call_count == 1
    assert mock_orcid_client.set_webhook.call_args[0][0] == '0000-0002-1825-0097'
    assert mock_orcid_client.set_webhook.call_args[0][1] == 'http://localhost/orcid-webhook/{}' \
        .format(url_safe_serializer.dumps('0000-0002-1825-0097'))

@skip("lsh@2022-11: webhooks no longer set on profile updates #7933")
def test_it_sets_a_webhook_when_a_profile_is_updated(profile: Profile,
                                                     orcid_config: Dict[str, str],
                                                     mock_orcid_client: MagicMock,
                                                     session: scoped_session,
                                                     url_safe_serializer: URLSafeSerializer,
                                                     commit: Callable[[], None]):
    session.add(profile)
    commit()

    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client,
                                                url_safe_serializer)
    models_committed.connect(receiver=webhook_maintainer)

    profile.add_email_address('1@example.com')
    session.add(profile)
    commit()

    assert mock_orcid_client.set_webhook.call_count == 1
    assert mock_orcid_client.set_webhook.call_args[0][0] == '0000-0002-1825-0097'
    assert mock_orcid_client.set_webhook.call_args[0][1] == 'http://localhost/orcid-webhook/{}' \
        .format(url_safe_serializer.dumps('0000-0002-1825-0097'))

def test_it_DOES_NOT_set_a_webhook_when_a_profile_is_updated(profile: Profile,
                                                     orcid_config: Dict[str, str],
                                                     mock_orcid_client: MagicMock,
                                                     session: scoped_session,
                                                     url_safe_serializer: URLSafeSerializer,
                                                     commit: Callable[[], None]):
    session.add(profile)
    commit()

    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client,
                                                url_safe_serializer)
    models_committed.connect(receiver=webhook_maintainer)

    profile.add_email_address('1@example.com')
    session.add(profile)
    commit()

    assert mock_orcid_client.set_webhook.call_count == 0

def test_it_will_remove_the_webhook_when_a_profile_is_deleted(profile: Profile,
                                                              orcid_config: Dict[str, str],
                                                              mock_orcid_client: MagicMock,
                                                              session: scoped_session,
                                                              url_safe_serializer:
                                                              URLSafeSerializer,
                                                              commit: Callable[[], None]):
    session.add(profile)
    commit()

    mock_orcid_client.remove_webhook.side_effect = Exception('Some Exception')
    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client,
                                                url_safe_serializer)
    models_committed.connect(receiver=webhook_maintainer)

    session.delete(profile)
    commit()

    assert mock_orcid_client.remove_webhook.call_count == 1


def test_it_ignores_other_models_being_committed(orcid_token: OrcidToken,
                                                 orcid_config: Dict[str, str],
                                                 mock_orcid_client: MagicMock,
                                                 session: scoped_session,
                                                 url_safe_serializer: URLSafeSerializer):
    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client,
                                                url_safe_serializer)
    models_committed.connect(receiver=webhook_maintainer)

    session.add(orcid_token)
    session.commit()

    assert mock_orcid_client.set_webhook.call_count == 0
    assert mock_orcid_client.remove_webhook.call_count == 0


def test_exception_is_handled_by_catch_exception_decorator(profile: Profile,
                                                           orcid_config: Dict[str, str],
                                                           mock_orcid_client: MagicMock,
                                                           session: scoped_session,
                                                           url_safe_serializer: URLSafeSerializer,
                                                           commit: Callable[[], None]):
    mock_orcid_client.remove_webhook.side_effect = Exception('Some Exception')

    session.add(profile)
    commit()

    webhook_maintainer = maintain_orcid_webhook(orcid_config, mock_orcid_client,
                                                url_safe_serializer)
    models_committed.connect(receiver=webhook_maintainer)

    session.delete(profile)
    commit()

    assert mock_orcid_client.remove_webhook.call_count == 1
