from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User

from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Initialize Migrate
migrate = Migrate(app, db)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
