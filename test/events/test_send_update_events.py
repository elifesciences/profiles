from flask_sqlalchemy import models_committed
from iso3166 import countries

from profiles.events import send_update_events
from profiles.models import (
    Address,
    Affiliation,
    Date,
    EmailAddress
)


def test_it_will_send_event_for_profile_insert(app, mock_publisher, profile):
    event_publisher = send_update_events(publisher=mock_publisher)
    event_publisher(app, [(profile, 'insert')])

    assert mock_publisher.publish.called
    assert mock_publisher.publish.call_args[0] == ({'id': '12345678', 'type': 'profile'}, )


def test_it_will_send_event_for_profile_deleted(app, mock_publisher, profile):
    event_publisher = send_update_events(publisher=mock_publisher)
    event_publisher(app, [(profile, 'delete')])

    assert mock_publisher.publish.called
    assert mock_publisher.publish.call_args[0] == ({'id': '12345678', 'type': 'profile'}, )


def test_it_will_send_event_for_affiliation_insert(app, mock_publisher, profile):
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    profile.add_affiliation(affiliation)

    event_publisher = send_update_events(publisher=mock_publisher)
    event_publisher(app, [(affiliation, 'insert')])

    assert mock_publisher.publish.called
    assert mock_publisher.publish.call_args[0] == ({'id': '12345678', 'type': 'profile'}, )


def test_it_will_send_event_if_email_address_is_updated(app, session, mock_publisher, profile):
    profile.add_email_address('2@example.com')
    session.add(profile)
    session.commit()

    email_address = EmailAddress.query.filter_by(email='2@example.com').one()

    event_publisher = send_update_events(publisher=mock_publisher)
    event_publisher(app, [(email_address, 'update')])

    assert mock_publisher.publish.called
    assert mock_publisher.publish.call_args[0] == ({'id': '12345678', 'type': 'profile'},)


def test_it_only_sends_one_event_if_multiple_changes_are_detected(app, mock_publisher, profile):
    affiliation = Affiliation('1', Address(countries.get('gb'), 'City'), 'Organisation', Date(2017))

    profile.add_affiliation(affiliation)

    event_publisher = send_update_events(publisher=mock_publisher)
    event_publisher(app, [(affiliation, 'insert'), (profile, 'update')])

    assert mock_publisher.publish.call_count == 1
    assert mock_publisher.publish.call_args[0] == ({'id': '12345678', 'type': 'profile'},)


def test_it_has_a_valid_signal_handler_registered_on_app():
    registered_handler_names = [recv.__name__ for id_, recv in models_committed.receivers.items()]
    assert 'event_handler' in registered_handler_names
    assert 'webhook_maintainer' in registered_handler_names
