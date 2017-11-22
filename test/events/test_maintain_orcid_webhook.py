from urllib.parse import urlencode

from flask import Flask
from flask_sqlalchemy import models_committed
from requests import PreparedRequest
import requests_mock

from profiles.events import maintain_orcid_webhook
from profiles.models import OrcidToken, Profile
from profiles.orcid import OrcidClient


def test_it_sets_a_webhook_when_a_profile_is_inserted(app: Flask, profile: Profile,
                                                      orcid_client: OrcidClient):
    webhook_maintainer = maintain_orcid_webhook(orcid_client)

    with requests_mock.Mocker() as mocker:
        def token_text(request: PreparedRequest):
            return urlencode({
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
                'scope': '/webhook',
                'grant_type': 'client_credentials',
            }, doseq=True) == request.body

        mocker.post('http://www.example.com/oauth/token', additional_matcher=token_text,
                    json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg'})

        mocker.put('http://www.example.com/api/v2.0/0001-0002-1825-0097/webhook/'
                   'http%3A%2F%2Flocalhost%2Forcid-webhook%2F0001-0002-1825-0097',
                   request_headers={'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'})

        webhook_maintainer(app, [(profile, 'insert')])

    assert mocker.call_count == 2


def test_it_sets_a_webhook_when_a_profile_is_updated(app: Flask, profile: Profile,
                                                     orcid_client: OrcidClient):
    webhook_maintainer = maintain_orcid_webhook(orcid_client)

    with requests_mock.Mocker() as mocker:
        def token_text(request: PreparedRequest):
            return urlencode({
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
                'scope': '/webhook',
                'grant_type': 'client_credentials',
            }, doseq=True) == request.body

        mocker.post('http://www.example.com/oauth/token', additional_matcher=token_text,
                    json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg'})

        mocker.put('http://www.example.com/api/v2.0/0001-0002-1825-0097/webhook/'
                   'http%3A%2F%2Flocalhost%2Forcid-webhook%2F0001-0002-1825-0097',
                   request_headers={'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'})

        webhook_maintainer(app, [(profile, 'update')])

    assert mocker.call_count == 2


def test_it_will_remove_the_webhook_when_a_profile_is_deleted(app: Flask, profile: Profile,
                                                              orcid_client: OrcidClient):
    webhook_maintainer = maintain_orcid_webhook(orcid_client)

    with requests_mock.Mocker() as mocker:
        def token_text(request: PreparedRequest):
            return urlencode({
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
                'scope': '/webhook',
                'grant_type': 'client_credentials',
            }, doseq=True) == request.body

        mocker.post('http://www.example.com/oauth/token', additional_matcher=token_text,
                    json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg'})

        mocker.delete('http://www.example.com/api/v2.0/0001-0002-1825-0097/webhook/'
                      'http%3A%2F%2Flocalhost%2Forcid-webhook%2F0001-0002-1825-0097',
                      request_headers={'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'})

        webhook_maintainer(app, [(profile, 'delete')])

    assert mocker.call_count == 2


def test_it_only_requests_a_token_once(app: Flask, profile: Profile,
                                       orcid_client: OrcidClient):
    webhook_maintainer = maintain_orcid_webhook(orcid_client)

    with requests_mock.Mocker() as mocker:
        def token_text(request: PreparedRequest):
            return urlencode({
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
                'scope': '/webhook',
                'grant_type': 'client_credentials',
            }, doseq=True) == request.body

        mocker.post('http://www.example.com/oauth/token', additional_matcher=token_text,
                    json={'access_token': '1/fFAGRNJru1FTz70BzhT3Zg'})

        mocker.put('http://www.example.com/api/v2.0/0001-0002-1825-0097/webhook/'
                   'http%3A%2F%2Flocalhost%2Forcid-webhook%2F0001-0002-1825-0097',
                   request_headers={'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'})

        mocker.delete('http://www.example.com/api/v2.0/0001-0002-1825-0097/webhook/'
                      'http%3A%2F%2Flocalhost%2Forcid-webhook%2F0001-0002-1825-0097',
                      request_headers={'Authorization': 'Bearer 1/fFAGRNJru1FTz70BzhT3Zg'})

        webhook_maintainer(app, [(profile, 'insert'), (profile, 'delete')])

    assert mocker.call_count == 3


def test_it_ignores_other_models_being_committed(app: Flask, orcid_token: OrcidToken,
                                                 orcid_client: OrcidClient):
    webhook_maintainer = maintain_orcid_webhook(orcid_client)

    webhook_maintainer(app, [(orcid_token, 'delete')])


def test_it_has_a_valid_signal_handler_registered_on_app():
    registered_handler_names = [recv.__name__ for id_, recv in models_committed.receivers.items()]
    assert 'webhook_maintainer' in registered_handler_names
