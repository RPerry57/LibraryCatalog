from flask import Blueprint

edit_delete = Blueprint('edit_delete', __name__, template_folder='templates')

from . import routes