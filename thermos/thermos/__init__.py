__author__ = 'Alex_lai'

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# add authentication
from flask_login import LoginManager

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# set up sercret_key for flash
app.config['SECRET_KEY'] = '\xa6\x90!\xdc\x98\xfc\xcd\xdbmz\xd22D\xf0\xb8\xb6\x93\xf0\rO\xd4\xf7\xca\xa5'

# set up database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'thermos.db')
app.config['DEBUG'] = True

db = SQLAlchemy(app)

# configure authentication
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.init_app(app)


import DBmodel
import controllers
