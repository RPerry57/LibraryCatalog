from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from .index import index
from .user_prof import user_prof
from .logreg import logreg
from .edit import edit
from .delete import delete

app.register_blueprint(index)
app.register_blueprint(user_prof)
app.register_blueprint(logreg)
app.register_blueprint(edit)
app.register_blueprint(delete)
