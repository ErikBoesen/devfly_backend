from flask import Blueprint, request, abort, g

from app import app, db
from app.models import User, Project
from app.util import to_json, succ, fail, get_now

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


@api_bp.route('/users')
def api_users():
    users = User.query.all()
    return to_json(users)


@api_bp.route('/users/<user_id>')
def api_user(user_id):
    user = User.query.get_or_404(user_id)
    return to_json(user)


@api_bp.route('/users/<user_id>/projects')
def api_user_projects(user_id):
    user = User.query.get_or_404(user_id)
    return to_json(user.projects)


@api_bp.route('/projects')
def api_projects():
    projects = Project.query.all()
    return to_json(projects)


@api_bp.route('/projects', methods=['POST'])
def api_project_create():
    # TODO: verify security implications
    project = Project(user_id=g.user.id, created_at=get_now(), **g.json)
    db.session.add(project)
    db.session.commit()
    return to_json(project)


@api_bp.route('/projects/<project_id>')
def api_project():
    project = Project.query.get_or_404(project_id)
    return to_json(project)


@api_bp.route('/projects/<project_id>', methods=['PUT'])
def api_project_update():
    project = Project.query.get_or_404(project_id)
    project.update(g.json)
    db.session.commit()
    return to_json(project)
