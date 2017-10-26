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
from profiles.commands import update_profile_from_orcid_record
from profiles.exceptions import ClientInvalidRequest, ClientInvalidScope, \
    ClientUnsupportedResourceType, InvalidClient, InvalidGrant, InvalidRequest, \
    OrcidTokenNotFound, ProfileNotFound, UnsupportedGrantType
from profiles.models import Name, OrcidToken, Profile
from profiles.orcid import OrcidClient
from profiles.repositories import OrcidTokens, Profiles
from profiles.utilities import expires_at, remove_none_values

LOGGER = logging.getLogger(__name__)


def create_blueprint(orcid: Dict[str, str], clients: Clients, profiles: Profiles,
                     orcid_client: OrcidClient, orcid_tokens: OrcidTokens) -> Blueprint:
    blueprint = Blueprint('oauth', __name__)

    @blueprint.route('/authorize')
    def _authorize() -> Response:
        if 'client_id' not in request.args:
            raise BadRequest('Invalid client_id')

        try:
            client = clients.find(request.args.get('client_id'))
        except KeyError as exception:
            raise BadRequest('Invalid client_id') from exception

        if request.args.get('redirect_uri', client.redirect_uri) != client.redirect_uri:
            raise BadRequest('Invalid redirect_uri')

        if not request.args.get('response_type'):
            raise ClientInvalidRequest(client, 'Missing response_type')
        elif request.args.get('response_type') != 'code':
            raise ClientUnsupportedResourceType(client)

        if request.args.get('scope'):
            raise ClientInvalidScope(client)

        state = remove_none_values({
            'redirect_uri': client.redirect_uri,
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

        if state['redirect_uri'] != client.redirect_uri:
            raise BadRequest('Invalid state (redirect_uri)')

        query = remove_none_values(OrderedDict([
            ('code', request.args.get('code')),
            ('error', request.args.get('error')),
            ('error_description', request.args.get('error_description')),
            ('state', state.get('original')),
        ]))

        return redirect('{}?{}'.format(client.redirect_uri, urlencode(query, True)), code=302)

    @blueprint.route('/token', methods=['POST'])
    def _token() -> Response:
        if 'client_id' not in request.form:
            raise InvalidClient

        try:
            client = clients.find(request.form.get('client_id'))
        except KeyError as exception:
            raise InvalidClient from exception

        if request.form.get('client_secret') != client.client_secret:
            raise InvalidClient
        elif request.form.get('redirect_uri') != client.redirect_uri:
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

        try:
            profile = profiles.get_by_orcid(json_data['orcid'])
            if json_data['name']:
                profile.name = Name(json_data['name'])
        except ProfileNotFound:
            if not json_data['name']:
                raise InvalidRequest('No name visible')
            profile = Profile(profiles.next_id(), Name(json_data['name']), json_data['orcid'])
            profiles.add(profile)

        json_data['id'] = profile.id

        try:
            orcid_token = orcid_tokens.get(json_data['orcid'])
            orcid_token.access_token = json_data['access_token']
            orcid_token.expires_at = expires_at(json_data['expires_in'])
        except OrcidTokenNotFound:
            orcid_token = OrcidToken(json_data['orcid'], json_data['access_token'],
                                     expires_at(json_data['expires_in']))
            orcid_tokens.add(orcid_token)

        try:
            orcid_record = orcid_client.get_record(profile.orcid, orcid_token.access_token)
            update_profile_from_orcid_record(profile, orcid_record)
        except RequestException as exception:
            LOGGER.exception(exception)
        except (LookupError, TypeError, ValueError) as exception:
            # We appear to be misunderstanding the ORCID data structure, but let's not block the
            # authentication flow.
            LOGGER.exception(exception)

        return make_response(jsonify(json_data), response.status_code)

    return blueprint
