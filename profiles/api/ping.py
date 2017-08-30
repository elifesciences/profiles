from flask import Blueprint

PING_BP = Blueprint('ping', __name__)


@PING_BP.route('/ping')
def ping():
    return ('pong', {'Content-Type': 'text/plain; charset=UTF-8',
                     'Cache-Control': 'must-revalidate, no-cache, no-store, private'})
