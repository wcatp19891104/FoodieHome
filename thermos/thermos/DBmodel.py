from datetime import datetime

from thermos import db
from sqlalchemy import desc

# set up authentication for User class
from flask_login import UserMixin

# create and verify password
from werkzeug.security import check_password_hash, generate_password_hash

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.Text, nullable = False)
    date = db.Column(db.DateTime, default = datetime.utcnow)
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def getRecentBookmarks(num):
        return Bookmark.query.order_by(desc(Bookmark.date)).limit(num)

    @staticmethod
    def getAllBookmarks(user):
        return Bookmark.query.filter_by(user_id = user.id).all()

    def __repr__(self):
        return "<Bookmark '{}': '{}'>".format(self.url, self.description)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True)
    email = db.Column(db.String(100), unique = True)
    # set the backref = user.. so in Bookmark it can use the User class named user. Don't need to use user_id
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')
    # this will stored the hashvalue for password
    password_hash = db.Column(db.String)

    # can only write not read, and this will not be stored in DB
    @property
    def password(self):
        raise AttributeError('Password is write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username= username).first()

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def get_by_userid(userid):
        return User.query.get(int(userid))
