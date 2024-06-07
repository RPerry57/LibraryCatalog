from flask import Blueprint

user_prof = Blueprint('user_prof', __name__, template_folder='templates')

from . import routes