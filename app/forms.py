from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
import sqlalchemy as s_alch
from app import db
from .models import User, Book

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
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
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    date_of_purchase = DateField('Date of Purchase', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(min=0, max=140)])
    submit = SubmitField('Add')

class EditBookForm(FlaskForm):
    book_id = StringField('Book ID', validators=[DataRequired()])
    title = StringField('Title')
    author = StringField('Author')
    date_of_purchase = DateField('Date of Purchase', validators=[Optional()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Edit')

class DeleteBookForm(FlaskForm):
    book_id = StringField('Book ID', validators=[DataRequired()])
    submit = SubmitField('Delete')

class OptionForm(FlaskForm):
    submit_add = SubmitField('Add')
    submit_edit = SubmitField('Edit')
    submit_delete = SubmitField('Delete')
    
class ExportForm(FlaskForm):
    target_email = StringField('eMail', validators=[DataRequired()])
    submit = SubmitField('Export')
    
class VerifyForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Submit')