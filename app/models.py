from flask_login import \
    UserMixin  # TODO: find out what UserMixin does and what can i do to not use and make my Users class more verbose.
from . import db
# from . import login_manager  # TODO: understand what login manager does
from werkzeug.security import generate_password_hash, \
    check_password_hash  # TODO: check and see if can change the strength of the hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask import current_app


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_title = db.Column(db.String(64), nullable=True)
    year_1 = db.Column(db.Float(), nullable=True)
    year_2 = db.Column(db.Float(), nullable=True)
    year_3 = db.Column(db.Float(), nullable=True)
    year_4 = db.Column(db.Float(), nullable=True)
    year_5 = db.Column(db.Float(), nullable=True)
    justification = db.Column(db.String(64), nullable=True)
    comments = db.Column(db.String(64), nullable=True)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    token = db.Column(db.String(64), unique=True)
    

# @db.event.listens_for(User, "after_insert")
# def insert_order_to_printer(mapper, connection, target):
#     print('New User', target.username)
