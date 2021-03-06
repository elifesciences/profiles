import json

from flask import Blueprint, make_response, request
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.wrappers import Response

from profiles.exceptions import ProfileNotFound
from profiles.repositories import Profiles
from profiles.serializer.normalizer import normalize, normalize_restricted, normalize_snippet
from profiles.utilities import cache

ORDER_ASC = 'asc'
ORDER_DESC = 'desc'

DEFAULT_ORDER = ORDER_DESC
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20


def create_blueprint(profiles: Profiles) -> Blueprint:
    blueprint = Blueprint('api', __name__)

    @blueprint.route('/profiles')
    @cache()
    def _list() -> Response:
        page = request.args.get('page', DEFAULT_PAGE, type=int)
        per_page = request.args.get('per-page', DEFAULT_PER_PAGE, type=int)
        order = request.args.get('order', DEFAULT_ORDER)

        if page < 1:
            raise BadRequest('Page less than 1')
        elif str(page) != str(request.args.get('page', DEFAULT_PAGE)):
            raise BadRequest('Invalid page')

        if per_page < 1 or per_page > 100:
            raise BadRequest('Per page out of range')
        elif str(per_page) != str(request.args.get('per-page', DEFAULT_PER_PAGE)):
            raise BadRequest('Invalid per page')

        if order not in [ORDER_ASC, ORDER_DESC]:
            raise BadRequest('Invalid order')

        total = len(profiles)
        profile_list = profiles.list(per_page, (page * per_page) - per_page, order == ORDER_DESC)

        if page > 1 and not profile_list:
            raise NotFound('No page %s' % page)

        response = make_response(json.dumps({'total': total, 'items': profile_list},
                                            default=normalize_snippet))

        response.headers['Content-Type'] = 'application/vnd.elife.profile-list+json;version=1'
        response.headers['Vary'] = 'Accept'

        return response

    @blueprint.route('/profiles/<profile_id>')
    @cache()
    def _get(profile_id: str) -> Response:
        try:
            profile = profiles.get(profile_id)
        except ProfileNotFound as exception:
            raise NotFound(str(exception)) from exception

        if 'view-restricted-profiles' in request.headers.get('x-consumer-groups', '').lower():
            response = make_response(json.dumps(profile, default=normalize_restricted))
        else:
            response = make_response(json.dumps(profile, default=normalize))
        response.headers['Content-Type'] = 'application/vnd.elife.profile+json;version=1'
        response.headers['Vary'] = 'Accept'

        return response

    return blueprint
