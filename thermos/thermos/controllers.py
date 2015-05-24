from datetime import datetime, tzinfo, timedelta

from flask import render_template, url_for, redirect, flash, request
import pytz

from form import BookmarkForm, LoginForm, SignUpForm
from thermos.DBmodel import User, Bookmark
from thermos import app, db, login_manager

from flask_login import login_required, login_user, logout_user, current_user

# using this info to store different timezone in DB, but it's not efficient
class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

GMT = Zone(0,False,'GMT')
PST = Zone(-8,False,'PST')
EST = Zone(-5,False,'EST')

# using pytz to change timezone based on the UTC time stored in DB
LATime = 'America/Los_Angeles'
localFormat = "%Y-%m-%d %H:%M:%S %Z"

bookmarks=[]

def store_bookmark(url, timezone, des):
    bookmarks.append(dict(
        url = url,
        usr = "alex",
        description = des,
        udate = datetime.utcnow(),
        LocalDate = datetime.now(timezone).strftime('%m/%d/%Y %H:%M:%S %Z')
    ))

def get_recent_bookmarks(num):
    list = sorted(bookmarks, key = lambda bm:bm['udate'], reverse=True)[:num]
    return list

# fake login user
def logged_in_user():
    # return User.query.filter_by(username='alex').first()
    pass

@app.route('/')
@app.route('/index')
def index():
    #recentbms = get_recent_bookmarks(3)
    recentbms = Bookmark.getRecentBookmarks(3)
    localtimelist = []
    namelist = []
    for bm in recentbms:
        localtimelist.append(bm.date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(LATime)).strftime(localFormat))
        namelist.append(User.get_by_userid(bm.user_id).username)
        # app.logger.debug(User.get_by_userid(bm.user_id))

    return render_template(('index.html'), recentbms = recentbms, timezone=PST, localtimelist=localtimelist, namelist = namelist)

@app.route('/user')
def user():
    allbms = Bookmark.getAllBookmarks(current_user)
    return render_template(('user.html'), usr=current_user, allbms = allbms)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

# if this url need to support post and get method,
# it need to specify the methods in the route
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = BookmarkForm()
    if form.validate_on_submit():
        url = form.url.data
        description = form.description.data
        # store_bookmark(url, PST, description)
        bm = Bookmark(url = url, description=description, user=current_user )
        db.session.add(bm)
        db.session.commit()
        flash("A new bookmark '{}' has been stored! ".format(description))
        return redirect(url_for('index'))
    else:
        # flash_errors(form)  show the error message by using flash
        return render_template('add.html', form=form)

# as long as I use login_user which import from flask_login
# I need to get the object from DB, cannot just use user_id stored in session
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        m_usr = User.get_by_username(form.username.data)
        # app.logger.debug(m_usr)

        if m_usr is not None and m_usr.check_password(form.password.data):
            # set flask-login to remember the user's ID in HTTP session
            login_user(m_usr, form.remember_me.data)
            flash("{} login successfully!".format(m_usr.username))
            # after login successfully it can direct back add view
            return redirect(request.args.get('next') or url_for('index'))
        flash('User Inputs are not match!')
    return render_template("login.html", form= form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        # # store new user in database
        user = User(username = form.username.data, email = form.email.data, password = form.password.data)
        db.session.add(user)
        db.session.commit()

        m_usr = User.get_by_username(form.username.data)
        if m_usr is not None:
        # set flask-login to remember the user's ID in HTTP session
            login_user(m_usr)
            flash("{} sign up successfully!".format(m_usr.username))
            return redirect(url_for('user'))
        flash('Signup fails & Internal error with database!')
    return render_template("signup.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/usr/<username>')
def usr(username):
    usr = User.query.filter_by(username = username).first_or_404()
    return render_template('user.html', usr = usr)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
