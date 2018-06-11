import logging
from collections import OrderedDict
from json import JSONDecodeError, dumps
from typing import Dict
from urllib.parse import urlencode

from flask import Blueprint, json, jsonify, make_response, redirect, request, url_for
import requests
from requests import RequestException
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Response

from profiles.clients import Clients
from profiles.commands import extract_email_addresses, update_profile_from_orcid_record
from profiles.exceptions import ClientInvalidRequest, ClientInvalidScope, \
    ClientUnsupportedResourceType, InvalidClient, InvalidGrant, InvalidRequest, \
    OrcidTokenNotFound, ProfileNotFound, UnsupportedGrantType
from profiles.models import Name, OrcidToken, Profile
from profiles.orcid import OrcidClient
from profiles.repositories import OrcidTokens, Profiles
from profiles.utilities import expires_at, no_cache, remove_none_values

LOGGER = logging.getLogger(__name__)


def create_blueprint(orcid: Dict[str, str], clients: Clients, profiles: Profiles,
                     orcid_client: OrcidClient, orcid_tokens: OrcidTokens) -> Blueprint:
    blueprint = Blueprint('oauth', __name__)

    @blueprint.route('/authorize')
    @no_cache
    def _authorize() -> Response:
        if 'client_id' not in request.args:
            raise BadRequest('Invalid client_id')

        try:
            client = clients.find(request.args.get('client_id'))
        except KeyError as exception:
            raise BadRequest('Invalid client_id') from exception

        redirect_uri = request.args.get('redirect_uri', client.canonical_uri())
        if redirect_uri not in client.redirect_uris:
            raise BadRequest('Invalid redirect_uri')

        if not request.args.get('response_type'):
            raise ClientInvalidRequest(client, 'Missing response_type')
        elif request.args.get('response_type') != 'code':
            raise ClientUnsupportedResourceType(client)

        if request.args.get('scope'):
            raise ClientInvalidScope(client)

        state = remove_none_values({
            'redirect_uri': redirect_uri,
            'client_id': client.client_id,
            'original': request.args.get('state')
        })

        return redirect(
            orcid['authorize_uri'] + '?' + urlencode({
                'client_id': orcid['client_id'],
                'response_type': request.args.get('response_type'),
                'scope': '/read-limited',
                'redirect_uri': url_for('oauth._check', _external=True),
                'state': dumps(state, sort_keys=True)
            }, True),
            code=302)

    @blueprint.route('/check')
    @no_cache
    def _check() -> Response:
        if not any(parameter in request.args for parameter in ['code', 'error']):
            raise BadRequest('Invalid code')

        try:
            state = json.loads(request.args.get('state'))
        except (JSONDecodeError, TypeError) as exception:
            raise BadRequest('Invalid state') from exception

        try:
            client = clients.find(state['client_id'])
        except KeyError as exception:
            raise BadRequest('Invalid state (client_id)') from exception

        if state['redirect_uri'] not in client.redirect_uris:
            raise BadRequest('Invalid state (redirect_uri)')

        query = remove_none_values(OrderedDict([
            ('code', request.args.get('code')),
            ('error', request.args.get('error')),
            ('error_description', request.args.get('error_description')),
            ('state', state.get('original')),
        ]))

        return redirect('{}?{}'.format(state['redirect_uri'], urlencode(query, True)), code=302)

    @blueprint.route('/token', methods=['POST'])
    @no_cache
    def _token() -> Response:
        if 'client_id' not in request.form:
            raise InvalidClient

        try:
            client = clients.find(request.form.get('client_id'))
        except KeyError as exception:
            raise InvalidClient from exception

        redirect_uri = request.form.get('redirect_uri')
        if request.form.get('client_secret') != client.client_secret:
            raise InvalidClient
        elif redirect_uri not in client.redirect_uris:
            raise InvalidRequest('Invalid redirect_uri')
        elif request.form.get('grant_type') != 'authorization_code':
            raise UnsupportedGrantType
        elif 'code' not in request.form:
            raise InvalidGrant

        data = {
            'client_id': orcid['client_id'],
            'client_secret': orcid['client_secret'],
            'redirect_uri': url_for('oauth._check', _external=True),
            'grant_type': 'authorization_code',
            'code': request.form['code'],
        }

        response = requests.post(url=orcid['token_uri'],
                                 data=data,
                                 headers={'Accept': 'application/json'})

        json_data = json.loads(response.text)

        json_data = {key: json_data[key] for key in
                     ['access_token', 'expires_in', 'name', 'orcid', 'token_type']}

        if json_data.get('token_type').lower() != 'bearer':
            raise ValueError('Got token_type {}, expected Bearer'.format(
                json_data.get('token_type')))

        profile = _find_profile(json_data)
        json_data['id'] = profile.id
        _find_and_update_access_token(json_data)

        return make_response(jsonify(json_data), response.status_code)

    def _find_profile(token_data: dict) -> Profile:
        try:
            return profiles.get_by_orcid(token_data['orcid'])
        except ProfileNotFound:
            orcid_record = _fetch_orcid_record(token_data['orcid'], token_data['access_token'])
            email_addresses = [e['email'] for e in extract_email_addresses(orcid_record)]

            try:
                profile = profiles.get_by_email_address(*email_addresses)
            except ProfileNotFound:
                profile = _create_profile(token_data)

            profile.name = Name(token_data['name'])
            _update_profile(profile, orcid_record)

            return profile

    def _create_profile(token_data: dict) -> Profile:
        if not token_data['name']:
            raise InvalidRequest('No name visible')
        profile = Profile(profiles.next_id(), Name(token_data['name']), token_data['orcid'])

        return profiles.add(profile)

    def _find_and_update_access_token(token_data: dict) -> OrcidToken:
        try:
            orcid_token = orcid_tokens.get(token_data['orcid'])
            orcid_token.access_token = token_data['access_token']
            orcid_token.expires_at = expires_at(token_data['expires_in'])
        except OrcidTokenNotFound:
            orcid_token = OrcidToken(token_data['orcid'], token_data['access_token'],
                                     expires_at(token_data['expires_in']))
            orcid_tokens.add(orcid_token)

        return orcid_token

    def _fetch_orcid_record(orcid: str, access_token: str) -> dict:
        try:
            return orcid_client.get_record(orcid, access_token)
        except RequestException as exception:
            LOGGER.exception(exception)

        return {}

    def _update_profile(profile: Profile, orcid_record: dict) -> None:
        try:
            update_profile_from_orcid_record(profile, orcid_record)
        except (AttributeError, LookupError, TypeError, ValueError) as exception:
            # We appear to be misunderstanding the ORCID data structure, but let's not block the
            # authentication flow.
            LOGGER.exception(exception)

    return blueprint
