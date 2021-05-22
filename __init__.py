from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(config.Config)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/book_api'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SECRET_KEY'] = 'secret'

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .views import main
    app.register_blueprint(main)
    
    return app
