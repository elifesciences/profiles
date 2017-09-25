import json

from flask import Blueprint, make_response, request
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.wrappers import Response

from profiles.exceptions import ProfileNotFound
from profiles.repositories import Profiles
from profiles.serializer.normalizer import normalize

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20


def create_blueprint(profiles: Profiles) -> Blueprint:
    blueprint = Blueprint('api', __name__)

    @blueprint.route('/profiles')
    def _list() -> Response:
        page = request.args.get('page', DEFAULT_PAGE, type=int)
        per_page = request.args.get('per-page', DEFAULT_PER_PAGE, type=int)

        if page < 1:
            raise BadRequest('Page less than 1')
        elif str(page) != str(request.args.get('page', DEFAULT_PAGE)):
            raise BadRequest('Invalid page')

        if per_page < 1 or per_page > 100:
            raise BadRequest('Per page out of range')
        elif str(per_page) != str(request.args.get('per-page', DEFAULT_PER_PAGE)):
            raise BadRequest('Invalid per page')

        total = len(profiles)
        profile_list = profiles.list(per_page, (page * per_page) - per_page)

        if page > 1 and not profile_list:
            raise NotFound('No page %s' % page)

        response = make_response(
            json.dumps({'total': total, 'items': profile_list}, default=normalize))
        response.headers['Content-Type'] = 'application/vnd.elife.profile-list+json;version=1'

        return response

    @blueprint.route('/profiles/<profile_id>')
    def _get(profile_id: str) -> Response:
        try:
            profile = profiles.get(profile_id)
        except ProfileNotFound as exception:
            raise NotFound(str(exception)) from exception

        response = make_response(json.dumps(profile, default=normalize))
        response.headers['Content-Type'] = 'application/vnd.elife.profile+json;version=1'

        return response

    return blueprint
