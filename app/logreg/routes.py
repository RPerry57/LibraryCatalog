from flask import render_template, flash, redirect, url_for, request, Blueprint, abort, session
from flask_login import current_user, login_user, login_required, logout_user
import flask_mail as f_mail
from flask_mail import Message
from urllib.parse import urlsplit
import sqlalchemy as s_alch
import random

from app import app, db, mail
from ..forms import *
from ..models import *
from . import logreg

@logreg.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already signed in, return them to home page
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    # Create LoginForm
    form = LoginForm()

    # If the form is valid, attempt to log the user in
    if form.validate_on_submit():
        user = db.session.scalar(s_alch.select(User).where(User.username == form.username.data))

        # If the user was not found in the database OR if entered password does not match stored password
        if (user is None) or (not user.check_password(form.password.data)):
            flash('Invalid username or password!')
            return redirect(url_for('logreg.login'))

        # Protect against faulty values for remember_me
        remember_me = form.remember_me.data
        if type(remember_me) != bool:
            remember_me = False
            
        # Log the user in and send them to their profile
        login_user(user, remember=remember_me)
        return redirect(url_for('user_prof.user', username=current_user.username))

    # Unless a form has been submitted, return the Sign In page
    return render_template('login.html', title='Sign In', form=form)

@logreg.route('/logout')
def logout():
    # Log the user out and return them to home page
    logout_user()
    return redirect(url_for('index.index'))

@logreg.route('/register', methods=['GET', 'POST'])
def register():

    # If user is already signed in, return them to home page
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Store user data and verification code in flask's session dictionary
        session['username'] = form.username.data
        session['email'] = form.email.data
        session['password'] = form.password.data
        session['code'] = str(random.randint(100000, 999999))
        return redirect(url_for('logreg.verify'))
    return render_template('register.html', title='Register', form=form)

@logreg.route('/register/verify', methods=['GET', 'POST'])
def verify():
    # If user is already signed in, return them to home page
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    # Get variables from registration
    new_username = session.get('username', None)
    new_email = session.get('email', None)
    new_password = session.get('password', None)
    verification_code = session.get('code', None)

    # Create form
    form = VerifyForm()

    if form.validate_on_submit():
        if form.verification_code.data == verification_code:
            # If user enters the correct code, create their profile and sign them in

            # Check to make sure that two users are not trying to register the same name at the same time
            dupe_user = db.session.scalar(s_alch.select(User).where(User.username == new_username))

            if dupe_user != None:
                flash('Username has been taken, please try again!')
                return redirect(url_for('logreg.register'))

            else:
                user = User(username=new_username, email=new_email)
                user.set_password(new_password)
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=False)
                flash('Welcome to Library Catalog, ' + new_username + '!')

            # Flush out all user data from session dict
            session.clear()
            login_user(user, remember=False)
            return redirect(url_for('user_prof.user', username=current_user.username))
        else:
            # If verification fails, send them back to registration
            flash('Woops, wrong code! Please try again!')
            return redirect(url_for('logreg.register'))
    
    # Create and send verification email
    msg = Message('Library Catalog Account Verification', sender=app.config['ADMINS'][0], recipients=[new_email])
    msg.body = 'Hello, {}!\nYour verification code is: {}.\nIf you did not sign up for Library Catalog, please ignore this email.'.format(new_username, verification_code)
    mail.send(msg)
    return render_template('verify.html', title='Verification', form=form)





