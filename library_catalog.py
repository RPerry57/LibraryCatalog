import sqlalchemy as s_alch
import sqlalchemy.orm as s_orm
from app import app, db
from app.models import User, Book

@app.shell_context_processor
def make_shell_context():
    return {'s_alch': s_alch, 's_orm': s_orm, 'db': db, 'User': User, 'Book': Book}