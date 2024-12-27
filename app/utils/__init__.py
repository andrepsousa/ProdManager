from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__, template_folder=os.path.join(
        os.getcwd(), 'app', 'templates'))

    print("Template folder:", app.template_folder)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'sqlite:///produtos.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv(
        'JWT_SECRET_KEY')

    db.init_app(app)
    jwt.init_app(app)

    from app.models.models import Product, User

    from app.routes.routes import main_bp
    app.register_blueprint(main_bp)

    return app
