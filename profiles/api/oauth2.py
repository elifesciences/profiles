from json import JSONDecodeError, dumps
from urllib.parse import urlencode
import requests
from flask import Blueprint, current_app, make_response, redirect, request, jsonify, url_for, json
from profiles.exceptions import ClientInvalidRequest, ClientUnsupportedResourceType, \
    ClientInvalidScope, InvalidClient, InvalidRequest, UnsupportedGrantType, InvalidGrant
from profiles.utilities import remove_none_values
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers import Response

OAUTH2_BP = Blueprint('oauth', __name__)


def find_client_by_id(client_id: str) -> dict:
    clients = current_app.config['config']['oauth2']['clients']

    try:
        (name, details) = next((k, v) for k, v in clients.items() if v['id'] == client_id)
    except StopIteration as exception:
        raise KeyError('No client with the client_id') from exception

    details['name'] = name

    return details


@OAUTH2_BP.route('/authorize')
def authorize() -> Response:
    if 'client_id' not in request.args:
        raise BadRequest('Invalid client_id')

    try:
        client = find_client_by_id(request.args.get('client_id'))
    except KeyError as exception:
        raise BadRequest('Invalid client_id') from exception

    if request.args.get('redirect_uri', client['redirect_uri']) != client['redirect_uri']:
        raise BadRequest('Invalid redirect_uri')

    if not request.args.get('response_type'):
        raise ClientInvalidRequest(client, 'Missing response_type')
    elif request.args.get('response_type') != 'code':
        raise ClientUnsupportedResourceType(client)

    if request.args.get('scope'):
        raise ClientInvalidScope(client)

    state = remove_none_values({
        'redirect_uri': client['redirect_uri'],
        'client_id': client['id'],
        'original': request.args.get('state')
    })

    return redirect(
        current_app.config['config']['oauth2']['server']['authorize_uri'] + '?' + urlencode({
            'client_id': current_app.config['config']['oauth2']['server']['client_id'],
            'response_type': request.args.get('response_type'),
            'scope': '/authenticate',
            'redirect_uri': url_for('oauth.check', _external=True, _scheme='https'),
            'state': dumps(state)
        }),
        code=302)


@OAUTH2_BP.route('/check')
def check() -> Response:
    if not any(parameter in request.args for parameter in ['code', 'error']):
        raise BadRequest('Invalid code')

    try:
        state = json.loads(request.args.get('state'))
    except (JSONDecodeError, TypeError) as exception:
        raise BadRequest('Invalid state') from exception

    try:
        client = find_client_by_id(state['client_id'])
    except KeyError as exception:
        raise BadRequest('Invalid state (client_id)') from exception

    if state['redirect_uri'] != client['redirect_uri']:
        raise BadRequest('Invalid state (redirect_uri)')

    query = remove_none_values({
        'code': request.args.get('code'),
        'error': request.args.get('error'),
        'error_description': request.args.get('error_description'),
        'state': state.get('original')
    })

    return redirect('{}?{}'.format(client['redirect_uri'], urlencode(query)), code=302)


@OAUTH2_BP.route('/token', methods=['POST'])
def token() -> Response:
    if 'client_id' not in request.form:
        raise InvalidClient

    try:
        client = find_client_by_id(request.form.get('client_id'))
    except KeyError as exception:
        raise InvalidClient from exception

    if request.form.get('client_secret') != client['secret']:
        raise InvalidClient
    elif request.form.get('redirect_uri') != client['redirect_uri']:
        raise InvalidRequest('Invalid redirect_uri')
    elif request.form.get('grant_type') != 'authorization_code':
        raise UnsupportedGrantType
    elif 'code' not in request.form:
        raise InvalidGrant

    data = {
        'client_id': current_app.config['config']['oauth2']['server']['client_id'],
        'client_secret': current_app.config['config']['oauth2']['server']['client_secret'],
        'redirect_uri': url_for('oauth.check', _external=True, _scheme='https'),
        'grant_type': 'authorization_code',
        'code': request.form['code'],
    }

    response = requests.post(url=current_app.config['config']['oauth2']['server']['token_uri'],
                             data=data,
                             headers={'Accept': 'application/json'})

    json_data = json.loads(response.text)

    if 'access_token' not in json_data:
        raise ValueError('No access_token')
    elif 'expires_in' not in json_data:
        raise ValueError('No expires_in')
    elif json_data.get('token_type').lower() != 'bearer':
        raise ValueError('Got token_type {}, expected Bearer'.format(json_data.get('token_type')))

    filtered_json_data = {your_key: json_data[your_key] for your_key in
                          ['access_token', 'expires_in', 'name', 'orcid', 'token_type']}

    return make_response(jsonify(filtered_json_data), response.status_code)
