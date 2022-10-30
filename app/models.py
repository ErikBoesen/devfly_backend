from app import app, db
import jwt
import datetime


class User(db.Model):
    __tablename__ = 'user'
    __serializable__ = ('id', 'email', 'first_name', 'last_name')

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    registered_at = db.Column(db.Integer)
    last_seen = db.Column(db.Integer)
    admin = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean)

    projects = db.relationship('Project', cascade='all,delete', back_populates='user')

    def __init__(self, id: str):
        self.id = id
        self.registered_at = now
        self.last_seen = now
        self.admin = False

    def generate_token(self):
        """
        Generate auth token.
        :return: token and expiration timestamp.
        """
        now = int(datetime.datetime.utcnow().timestamp())
        payload = {
            'iat': now,
            'sub': self.id,
        }
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
    __serializable__ = ('id', 'name', 'description', 'image_url')
    __editable__ = {'name', 'description', 'image_url'}

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, required=True)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)

    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='reports')

    def update(self, **new_values):
        accepted_values = {key: value for key, value in new_values.items() if key in self.__editable__}
        for key, value in accepted_values.items():
            setattr(self, key, value)
