from flask import Blueprint

ping_bp = Blueprint('ping', __name__)


@ping_bp.route('/ping')
def ping():
    return ('pong', {'Content-Type': 'text/plain; charset=UTF-8',
                     'Cache-Control': 'must-revalidate, no-cache, no-store, private'})
