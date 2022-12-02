from flask import Blueprint, request, abort, g

from app import app, db
from app.models import User, Project, Review
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
                g.user.last_seen = get_now()
                db.session.commit()
        if not g.user:
            return fail('You must be authenticated to use this endpoint.', 401)
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


@api_bp.route('/users/search/<query>')
def search_users(query):
    query = query.lower()
    users = User.query.filter(User.name.ilike('%' + query + '%')).all()
    return jsonify(users)


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
def api_project(project_id):
    project = Project.query.get_or_404(project_id)
    return to_json(project)


@api_bp.route('/projects/<project_id>', methods=['PUT'])
def api_project_update(project_id):
    project = Project.query.get_or_404(project_id)
    project.update(g.json)
    db.session.commit()
    return to_json(project)


@api_bp.route('/projects/search/<query>')
def search_projects(query):
    query = query.lower()
    projects = Project.query.filter(Project.name.ilike('%' + query + '%')).all()
    return jsonify(projects)


@api_bp.route('/projects/<project_id>/tags/<tag_name>', methods=['POST'])
def add_tag(project_id, tag_name):
    project = Project.query.get_or_404(project_id)
    tag_name = tag_name.lower()
    if not (g.me.admin or project.is_hosted_by(g.me)):
        abort(403)
    # First, check if the project already has this tag.
    if project.has_tag(tag_name):
        return fail('Project already has this tag.')
    if project.add_tag(tag_name):
        db.session.commit()
        return succ('Added tag!')
    # If the tag is blacklisted or there was another problem
    return fail('Tag not added.')


@api_bp.route('/projects/<project_id>/tags/<tag_name>', methods=['DELETE'])
def remove_tag(project_id, tag_name):
    project = Project.query.get_or_404(project_id)
    if not (g.me.admin or project.is_hosted_by(g.me)):
        abort(403)
    if not project.has_tag(tag_name):
        return fail('Project does not have this tag.')
    if project.remove_tag(tag_name):
        db.session.commit()
        return succ('Removed tag.')
    # Should not be reached, but just in case.
    return fail('Tag not removed.')


@api_bp.route('/tags/search/<query>')
def search_tags(query):
    query = query.lower()
    tags = Tag.query.filter(Tag.name.ilike('%' + query + '%'))
    return jsonify([tag.name for tag in tags])


# This is a kinda useless endpoint
"""
@api_bp.route('/projects/<project_id>/reviews')
def api_project_item_reviews(project_id):
    project = Project.query.get_or_404(project_id)
    return to_json(project.reviews)
"""


@api_bp.route('/projects/<project_id>/reviews', methods=['POST'])
def api_project_item_reviews_create(project_id):
    project = Project.query.get_or_404(project_id)
    review = Review.query.filter_by(user_id=g.me.id, project_id=project_id).first()
    if review is None:
        review = Review(created_at=get_now(), user_id=g.me.id, project_id=project_id)
        db.session.add()
        db.session.commit()
    project.update_like_count()
    return to_json(project.reviews)


@api_bp.route('/projects/<project_id>/reviews', methods=['DELETE'])
def api_project_item_reviews_delete(project_id):
    review = Review.query.filter_by(user_id=g.me.id, project_id=project_id).first_or_404()
    db.session.delete(review)
    db.session.commit()
    project.update_like_count()
    return succ('Review removed.')
