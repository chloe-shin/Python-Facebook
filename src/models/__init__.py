from src import db 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# create database model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False, unique=False)

    # password: 지금 입력한 비밀번호 #self.password: 사용자 비밀번호
    def generate_password(self, password):
        self.password = generate_password_hash(password)  # password를 암호화

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(20), nullable=False)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    like_time = db.Column(db.Integer, default = 0)

    def comments(self):
        return Comments.query.filter_by(post_id=self.id).all()


class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

