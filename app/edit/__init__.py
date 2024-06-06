from flask import Blueprint

edit = Blueprint('edit', __name__, template_folder='templates')

from . import routes