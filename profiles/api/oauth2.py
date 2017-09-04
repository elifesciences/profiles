from json import JSONDecodeError, dumps
from urllib.parse import urlencode
import requests
from flask import Blueprint, current_app, redirect, request, jsonify, url_for, json
from werkzeug.exceptions import BadRequest, Unauthorized

OAUTH2_BP = Blueprint('oauth', __name__)


def find_client_by_id(client_id):
    clients = current_app.config['config']['oauth2']['clients']

    try:
        (name, details) = next((k, v) for k, v in clients.items() if v['id'] == client_id)
    except StopIteration:
        raise KeyError('No client with the client_id')

    details['name'] = name

    return details


@OAUTH2_BP.route('/authorize')
def authorize():
    if 'client_id' not in request.args:
        raise BadRequest('Invalid client_id')

    try:
        client = find_client_by_id(request.args.get('client_id'))
    except KeyError:
        raise BadRequest('Invalid client_id')

    if request.args.get('redirect_uri') != client['redirect_uri']:
        raise BadRequest('Invalid redirect_uri')

    state = {
        'redirect_uri': client['redirect_uri'],
        'client_id': client['id'],
        'original': request.args.get('state', '')
    }

    return redirect(
        current_app.config['config']['oauth2']['server']['authorize_uri'] + '?' + urlencode({
            'client_id': current_app.config['config']['oauth2']['server']['client_id'],
            'response_type': 'code',
            'scope': current_app.config['config']['oauth2']['server']['scope'],
            'redirect_uri': url_for('oauth.check', _external=True),
            'state': dumps(state)
        }),
        code=302)


@OAUTH2_BP.route('/check')
def check():
    if 'code' not in request.args:
        raise BadRequest('Invalid code')

    try:
        state = json.loads(request.args.get('state'))
    except (JSONDecodeError, TypeError):
        raise BadRequest('Invalid state')

    try:
        client = find_client_by_id(state['client_id'])
    except KeyError:
        raise BadRequest('Invalid state (client_id)')

    if state['redirect_uri'] != client['redirect_uri']:
        raise BadRequest('Invalid state (redirect_uri)')
    elif 'original' not in state:
        raise BadRequest('Invalid state (original)')

    return redirect(
        client['redirect_uri'] + '?' + urlencode({
            'code': request.args.get('code'),
            'state': state['original']
        }),
        code=302)


@OAUTH2_BP.route('/token', methods=['POST'])
def token():
    if 'client_id' not in request.form:
        raise BadRequest('Invalid client_id')

    try:
        client = find_client_by_id(request.form.get('client_id'))
    except KeyError:
        raise BadRequest('Invalid client_id')

    if request.form.get('client_secret') != client['secret']:
        raise BadRequest('Invalid client_secret')
    elif request.form.get('redirect_uri') != client['redirect_uri']:
        raise BadRequest('Invalid redirect_uri')
    elif request.form.get('grant_type') != 'authorization_code':
        raise BadRequest('Invalid grant_type')
    elif 'code' not in request.form:
        raise BadRequest('Invalid code')

    data = {
        'client_id': current_app.config['config']['oauth2']['server']['client_id'],
        'client_secret': current_app.config['config']['oauth2']['server']['client_secret'],
        'redirect_uri': url_for('oauth.check', _external=True),
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
    elif json_data.get('token_type') != 'Bearer':
        raise ValueError('Got token_type ' + json_data.get('token_type') +
                         ', expected Bearer')

    filtered_json_data = {your_key: json_data[your_key] for your_key in
                          ['access_token', 'expires_in', 'token_type']}

    return jsonify(filtered_json_data), response.status_code


@OAUTH2_BP.route('/user')
def user():
    if 'Authorization' not in request.headers:
        raise Unauthorized('Requires authorization')

    response = requests.get(url=current_app.config['config']['oauth2']['server']['user_uri'],
                            headers={'Authorization': request.headers['Authorization']})

    return response.text, response.status_code, {'Content-Type': response.headers['Content-Type']}
