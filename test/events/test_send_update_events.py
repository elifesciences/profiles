from unittest.mock import MagicMock, patch

from flask_sqlalchemy import models_committed
from iso3166 import countries
from sqlalchemy.orm import scoped_session

from profiles.events import send_update_events
from profiles.models import (
    Address,
    Affiliation,
    Date,
    Profile,
)


def test_it_has_a_valid_signal_handler_registered_on_app():
    registered_handler_names = [recv.__name__ for id_, recv in models_committed.receivers.items()
                                if recv.__name__]
    assert 'event_handler' in registered_handler_names


def test_it_will_send_event_for_profile_insert(mock_publisher, profile):
    event_publisher = send_update_events(publisher=mock_publisher)
    event_publisher({}, [(profile, 'insert')])

    assert mock_publisher.publish.called
    assert mock_publisher.publish.call_args[0] == ({'id': '12345678', 'type': 'profile'}, )


def test_it_will_send_event_for_profile_deleted(mock_publisher: MagicMock,
                                                profile: Profile) -> None:
    event_publisher = send_update_events(publisher=mock_publisher)
    event_publisher({}, [(profile, 'delete')])

    assert mock_publisher.publish.called
    assert mock_publisher.publish.call_args[0] == ({'id': '12345678', 'type': 'profile'}, )


def test_it_will_send_event_for_affiliation_insert(mock_publisher: MagicMock, profile: Profile,
                                                   session: scoped_session) -> None:
    event_publisher = send_update_events(publisher=mock_publisher)
    models_committed.connect(receiver=event_publisher)

    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    profile.add_affiliation(affiliation)
    session.add(profile)

    with patch('profiles.orcid.request'):
        session.commit()

    assert mock_publisher.publish.call_count == 1
    assert mock_publisher.publish.call_args[0][0] == {'id': '12345678', 'type': 'profile'}


def test_it_will_send_event_if_email_address_is_updated(mock_publisher: MagicMock, profile: Profile,
                                                        session: scoped_session):
    event_publisher = send_update_events(publisher=mock_publisher)
    models_committed.connect(receiver=event_publisher)

    profile.add_email_address('2@example.com')
    session.add(profile)

    with patch('profiles.orcid.request'):
        session.commit()

    assert mock_publisher.publish.call_count == 1
    assert mock_publisher.publish.call_args[0][0] == {'id': '12345678', 'type': 'profile'}


def test_it_only_sends_one_event_if_multiple_changes_are_detected(mock_publisher: MagicMock,
                                                                  profile: Profile,
                                                                  session: scoped_session) -> None:
    event_publisher = send_update_events(publisher=mock_publisher)
    models_committed.connect(receiver=event_publisher)

    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))
    profile.add_affiliation(affiliation)
    session.add(profile)

    with patch('profiles.orcid.request'):
        session.commit()

    assert mock_publisher.publish.call_count == 1
    assert mock_publisher.publish.call_args[0][0] == {'id': '12345678', 'type': 'profile'}
