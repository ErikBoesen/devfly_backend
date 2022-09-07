from flask import Blueprint, request, abort, g

from app import app, db
#from app.models import
from app.util import to_json, succ, fail

import datetime


api_bp = Blueprint('api', __name__)


@api_bp.errorhandler(404)
def not_found(error):
    return fail('Not found.', 404)


@api_bp.errorhandler(401)
def unauthorized(error):
    return fail('You\'re not authorized to perform this action.', 401)


@api_bp.errorhandler(403)
def forbidden(error):
    return fail('You don\'t have permission to do this.', 403)


@api_bp.errorhandler(500)
def internal(error):
    return fail('Internal server error.', 500)


@api_bp.before_request
def setup_request():
    g.user = None
    g.json = None
    if request.method != 'OPTIONS':
        token = request.headers.get('Authorization')
        if token is not None:
            token = token.split(' ')[-1]
            g.user = User.from_token(token)
            if g.user is not None:
                g.user.last_seen = int(datetime.datetime.utcnow().timestamp())
                db.session.commit()
        try:
            g.json = request.get_json()
        except Exception as e:
            g.json = None
        print('User: ' + (g.user.email if g.user else 'anonymous'))


def requires_login(f):
    @wraps(f)
    def wrapper_requires_login(*args, **kwargs):
        if g.user is None:
            return fail('Endpoint requires valid Authorization header.', code=401)
        return f(*args, **kwargs)
    return wrapper_requires_login


@api_bp.route('/test')
def api_test():
    content = {'hi': 'this is a very quirky API endpoint'}
    return to_json(content)
