from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField
from flask.ext.wtf.html5 import URLField
from wtforms.validators import DataRequired, url, InputRequired, Length, Regexp, EqualTo, Email
from wtforms import validators, ValidationError

from thermos.DBmodel import User
from thermos import app

class BookmarkForm(Form):
    # customized validation function
    def validate_len(form, field):
        if len(field.data) > 15 or len(field.data) < 1:
            raise ValidationError('The length of description should be [1,15]')

    # using html5 url field
    url = URLField('New URL: ', validators=[DataRequired(), url()])
    description = StringField('Description: ', [validate_len])

    # customized the validation function
    # override the validate function
    # this will be called when validate_on_submit
    def validate(self):

        if not self.url.data.startswith("http://") or \
            self.url.data.startswith("https://"):
            self.url.data = "http://" + self.url.data


        # original validation check
        if not Form.validate(self):
            return False

        # make description not empty
        if not self.description.data:
            self.description.data = self.url.data

        return True

    # customized validation length
    # description = StringField('description', [InputRequired(), validate_len ] )

    # default validation
    # StringField('description', validators=[InputRequired(), Length(min=1, max=15)] )

class LoginForm(Form):
    username = StringField('Your Username: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    # submit = SubmitField('Log In')

class SignUpForm(Form):
    username = StringField('User Name: ', validators=[DataRequired(), Length(3, 50),
                                                      Regexp('^[A-Za-z0-9_]{3,}$', message ='username consists of numbers, letters and underscores')])
    password2 = PasswordField('Confirm Password: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired(), EqualTo('password2', message='Your passwords are not matched')] )
    email = StringField('Email: ', validators=[DataRequired(), Length(1, 50), Email()])

    def validate_email(self, email_field):
        # us = User.query.filter_by(email = email_field.data).first()
        # app.logger.debug(us)
        if User.query.filter_by(email = email_field.data).first():
            raise ValidationError('The email address has been signed up before.')
        return True

    def validate_username(self, username_field):
        if User.query.filter_by(username = username_field.data).first():
            raise ValidationError('The Username has been signed up before.')
        return True
