from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
import sqlalchemy as s_alch
from app import db
from .models import User, Book
import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=24)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=24)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=24)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=128)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=24)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=1, max=24), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(s_alch.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('That username is already in use, please try another!')
        
    def validate_email(self, email):
        user = db.session.scalar(s_alch.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('That email address is already in use, please try another!')

class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=128)])
    author = StringField('Author', validators=[DataRequired(), Length(min=1, max=128)])
    date_of_purchase = DateField('Date of Purchase', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(min=0, max=512)])
    submit = SubmitField('Add')

    def validate_date_of_purchase(self, date_of_purchase):
        if date_of_purchase.data > datetime.date.today():
            raise ValidationError('The date cannot be in the future!')

class EditBookForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=0, max=128)])
    author = StringField('Author', validators=[Length(min=0, max=128)])
    date_of_purchase = DateField('Date of Purchase', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Length(min=0, max=512)])
    submit = SubmitField('Edit')

    def validate_date_of_purchase(self, date_of_purchase):
        if date_of_purchase.data > datetime.date.today():
            raise ValidationError('The date cannot be in the future!')

class DeleteBookForm(FlaskForm):
    submit_yes = SubmitField('Yes')
    submit_no = SubmitField('No')

class AddForm(FlaskForm):
    submit_add = SubmitField('Add')

    
class ExportForm(FlaskForm):
    target_email = StringField('eMail', validators=[DataRequired(), Email(), Length(min=1, max=128)])
    submit = SubmitField('Export')
    
class VerifyForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Submit')
