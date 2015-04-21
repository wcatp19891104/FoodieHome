#! /usr/bin/env python

from thermos import app,db
from thermos.DBmodel import User
from flask.ext.script import Manager, prompt_bool

manager = Manager(app)

@manager.command
def initdb():
    db.create_all()
    db.session.add(User(username="alex",email="alex@gmail.com", password='test'))
    db.session.add(User(username="lai",email="lai@gmail.com", password='test'))
    db.session.commit()
    print 'Init DB'

@manager.command
def dropdb():
    if prompt_bool("Are you sure to delete DB"):
        db.drop_all()
        print 'Delete DB'

if __name__ == '__main__':
    manager.run()
