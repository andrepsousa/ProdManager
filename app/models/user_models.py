from app.utils import db
from app.models.models import User


def register_user(username, password, email):
    if User.query.filter_by(username=username).first():
        raise ValueError("Este usuário já existe.")
    if User.query.filter_by(email=email).first():
        raise ValueError("Email já cadastrado")

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user
