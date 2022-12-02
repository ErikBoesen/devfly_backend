from app import app, db, bcrypt
from app.util import get_now
import jwt
import datetime
import uuid


# Many-to-many relationships
taggings = db.Table('tagging',
    db.Column('project_id', db.String, db.ForeignKey('project.id'), nullable=False),
    db.Column('tag_name', db.String, db.ForeignKey('tag.name'), nullable=False),
)


class User(db.Model):
    __tablename__ = 'user'
    __serializable__ = ('id', 'username', 'email', 'first_name', 'last_name')

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    admin = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=False)
    confirmed = db.Column(db.Boolean)

    registered_at = db.Column(db.Integer)
    last_seen = db.Column(db.Integer)

    projects = db.relationship('Project', cascade='all,delete', back_populates='user')
    reviews = db.relationship('Review', cascade='all,delete', back_populates='user')

    def __init__(self, username: str, email: str, first_name: str, last_name: str, password: str):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)

        self.confirmed = False
        self.registered_at = get_now()
        self.last_seen = get_now()

    def is_password_correct(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def generate_token(self):
        """
        Generate auth token.
        :return: token and expiration timestamp.
        """
        payload = {
            'iat': get_now(),
            'sub': self.id,
        }
        print(jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        ))

        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def from_token(token):
        """
        Decode/validate an auth token.
        :param token: token to decode.
        :return: User whose token this is, or None if token invalid/no user associated
        """
        try:
            payload = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
            return User.query.get(payload['sub'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Signature expired, or token otherwise invalid
            return None


class Project(db.Model):
    __tablename__ = 'project'
    __serializable__ = ('id', 'name', 'description', 'image_url', 'like_count')
    __editable__ = {'name', 'description', 'image_url'}

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    github_url = db.Column(db.String)
    like_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)

    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='projects')

    reviews = db.relationship('Review', cascade='all,delete', back_populates='project')
    tags = db.relationship(
        'Tag', secondary=taggings, lazy='subquery',
        backref=db.backref('projects', lazy=True))

    def update(self, new_values):
        accepted_values = {key: value for key, value in new_values.items() if key in self.__editable__}
        for key, value in accepted_values.items():
            setattr(self, key, value)

    def has_tag(self, tag_name) -> bool:
        return self.tags.filter(taggings.c.tag_name == tag_name).count() > 0

    def add_tag(self, tag_name) -> bool:
        tag = Tag.query.get(tag_name)
        # Do we need to create the tag in the database?
        if tag is None:
            # Fail if the tag is blacklisted
            tag = Tag(tag_name)
            db.session.add(tag)
        self.tags.append(tag)
        return True

    def remove_tag(self, tag_name) -> bool:
        tag = Tag.query.get(tag_name)
        self.tags.remove(tag)
        return True

    def update_like_count(self):
        self.like_count = self.reviews.count()


class Tag(db.Model):
    __tablename__ = 'tag'

    name = db.Column(db.String(32), primary_key=True)


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)

    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='reviews')

    project_id = db.Column(db.String, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', back_populates='reviews')
