from flask import render_template, flash, redirect, url_for, request, Blueprint, abort
from flask_login import current_user, login_user, login_required, logout_user
import flask_mail as f_mail
from flask_mail import Message
from urllib.parse import urlsplit
import sqlalchemy as s_alch

from app import app, db, mail
from ..forms import *
from ..models import *
from . import index

@index.route('/')
@index.route('/index')
def index():
    # Basic home page. base.html includes links at top to help navigate the site, and index.html extends that template
    return render_template('index.html', title='Home')

