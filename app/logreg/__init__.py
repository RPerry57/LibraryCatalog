from flask import Blueprint

logreg = Blueprint('logreg', __name__, template_folder='templates')

from . import routes