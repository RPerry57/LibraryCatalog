from flask import Blueprint

delete = Blueprint('delete', __name__, template_folder='templates')

from . import routes