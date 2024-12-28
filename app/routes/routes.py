from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from flask import (
    Blueprint, jsonify, request, render_template, url_for, flash, redirect
    )
from app.models.product_models import (
    list_products, create_product, update_product,
    delete_product, product_by_id
    )
from app.models.user_models import register_user
from app.models.models import Product, User
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from datetime import timedelta
from werkzeug.exceptions import BadRequest

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    product = Product.query.all()
    return render_template('index.html', product=product)


@main_bp.route('/produtos', methods=['GET'], endpoint='get_products')
@login_required
def get_products():
    products = list_products()
    print("Products in get_products:", products)  # Debug print
    return render_template('product/list.html', products=products)


@main_bp.route('/produtos/<int:id_product>', methods=["GET"],
               endpoint='get_products_id')
@login_required
def get_products_id(id_product):
    try:
        product = product_by_id(id_product)
        return render_template('product/detail.html', product=product)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for('main.get_products'))
    except Exception as e:
        flash(f"Erro inesperado: {str(e)}", "danger")
        return redirect(url_for('main.get_products'))


@main_bp.route('/produtos/novo', methods=["GET", "POST"],
               endpoint='create_product_view')
@login_required
def create_product_view():
    if request.method == "GET":
        return render_template('product/create.html')

    try:
        data = request.form
        new_product_data = {
            "name": data["name"],
            "price": float(data["price"]),
            "description": data.get("description")
        }

        create_product(new_product_data)
        flash("Produto criado com sucesso.", "success")
        return redirect(url_for('main.get_products'))
    except KeyError as e:
        flash(f"Campo faltando na requisição: {str(e)}", "danger")
        return render_template('product/create.html')
    except Exception as e:
        flash(f"Erro ao criar o produto: {str(e)}", "danger")
        return render_template('product/create.html')


@main_bp.route('/produtos/<int:id_product>/editar', methods=["GET", "POST"],
               endpoint='update_product_view')
@login_required
def update_product_view(id_product):
    product = product_by_id(id_product)
    if request.method == "GET":
        return render_template('product/edit.html', product=product)

    try:
        data = request.form
        updated_data = {
            "name": data["name"],
            "price": float(data["price"]),
            "description": data.get("description")
        }

        update_product(id_product, updated_data)
        flash("Produto atualizado com sucesso.", "success")
        return redirect(url_for('main.get_products'))
    except ValueError as e:
        flash(str(e), "danger")
        return render_template('product/edit.html', product=product)
    except Exception as e:
        flash(f"Erro ao atualizar o produto: {str(e)}", "danger")
        return render_template('product/edit.html', product=product)


@main_bp.route('/produtos/<int:id_product>/deletar', methods=["GET", "POST"],
               endpoint='delete_product_view')
@login_required
def delete_product_view(id_product):
    product = product_by_id(id_product)
    if request.method == "GET":
        return render_template('product/delete.html', product=product)

    try:
        delete_product(id_product)
        flash("Produto deletado com sucesso!", "success")
        return redirect(url_for('main.get_products'))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for('main.get_products'))
    except Exception as e:
        flash(f"Erro ao deletar o produto: {str(e)}", "danger")
        return redirect(url_for('main.get_products'))


@main_bp.route('/cadastro', methods=["GET", "POST"],
               endpoint='register_view')
def register_view():
    if request.method == 'GET':
        return render_template("user/register.html")

    elif request.method == 'POST':
        try: 
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
        except BadRequest:
            flash("Formulário inválido", "danger")
            return render_template("user/register.html"), 400

        if not username or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("user/register.html"), 400

        try:
            user = register_user(
                username=username, email=email, password=password)
            login_user(user)
            flash("Usuário registrado com sucesso!", "success")
            return redirect(url_for('main.index'))
        except ValueError as e:
            flash(f"Erro: {e}", "danger")
            return render_template("user/register.html"), 400
        except Exception as e:
            flash(f"Erro inesperado: {str(e)}", "danger")
            return render_template("user/register.html"), 500

    return "Método não permitido", 405


@main_bp.route('/login', methods=["GET", "POST"],
               endpoint='login')
def login():
    '''if request.method == 'GET':
        return render_template("user/login.html")'''

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login bem-sucedido!", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Credenciais inválidas", "danger")
    return render_template("user/login.html")


@main_bp.route('/logout', methods=['GET', 'POST'],
               endpoint='logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('main.index'))
