from flask import Flask, session
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
db = SQLAlchemy()
jwt = JWTManager()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder=os.path.join(
        os.getcwd(), 'app', 'templates'))

    print("Template folder:", app.template_folder)

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///produtos.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.models.models import Product, User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=15)
        session.modified = True

    from app.routes.routes import main_bp
    app.register_blueprint(main_bp)

    return app
