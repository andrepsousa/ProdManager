# app/routes/routes.py
from flask import (
    Blueprint, jsonify, request, render_template,
    url_for, flash, redirect, session
)
from flask_login import login_user, login_required, logout_user
from werkzeug.exceptions import BadRequest

from app.models.product_models import (
    list_products, create_product, update_product,
    delete_product, product_by_id
)
from app.models.user_models import register_user
from app.models.models import Product, User
from app.security import require_oauth, has_role
from flask.typing import ResponseReturnValue

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    product = Product.query.all()
    return render_template('index.html', product=product)


@main_bp.route('/produtos', methods=['GET'], endpoint='get_products')
@login_required
def get_products():
    products = list_products()
    return render_template('product/list.html', products=products)


@main_bp.route('/produtos/<int:id_product>', methods=["GET"],
               endpoint='get_products_id')
@login_required
def get_products_id(id_product):
    try:
        product = product_by_id(id_product)
        return render_template('product/detail.html', product=product)
    except ValueError as e:
        flash(str(e), "product_danger")
        return redirect(url_for('main.get_products'))
    except Exception as e:
        flash(f"Erro inesperado: {str(e)}", "product_danger")
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
        flash("Produto criado com sucesso.", "product_success")
        return redirect(url_for('main.get_products'))
    except KeyError as e:
        flash(f"Campo faltando na requisição: {str(e)}", "product_danger")
        return render_template('product/create.html')
    except Exception as e:
        flash(f"Erro ao criar o produto: {str(e)}", "product_danger")
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
        flash("Produto atualizado com sucesso.", "product_success")
        return redirect(url_for('main.get_products'))
    except ValueError as e:
        flash(str(e), "product_danger")
        return render_template('product/edit.html', product=product)
    except Exception as e:
        flash(f"Erro ao atualizar o produto: {str(e)}", "product_danger")
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
        flash("Produto deletado com sucesso!", "product_success")
        return redirect(url_for('main.get_products'))
    except ValueError as e:
        flash(str(e), "product_danger")
        return redirect(url_for('main.get_products'))
    except Exception as e:
        flash(f"Erro ao deletar o produto: {str(e)}", "product_danger")
        return redirect(url_for('main.get_products'))


@main_bp.route('/cadastro', methods=["GET", "POST"], endpoint='register_view')
def register_view() -> ResponseReturnValue:
    if request.method == 'GET':
        return render_template("user/register.html")
    elif request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
        except BadRequest:
            flash("Formulário inválido", "register_danger")
            return render_template("user/register.html"), 400

        if not username or not email or not password:
            flash("Todos os campos são obrigatórios.", "register_danger")
            return render_template("user/register.html"), 400

        try:
            user = register_user(
                username=username, email=email, password=password)
            login_user(user)
            flash("Usuário registrado com sucesso!", "register_success")
            return redirect(url_for('main.index'))
        except ValueError as e:
            flash(f"Erro: {e}", "register_danger")
            return render_template("user/register.html"), 400
        except Exception as e:
            flash(f"Erro inesperado: {str(e)}", "register_danger")
            return render_template("user/register.html"), 500
        
    return "Method Not Allowed", 405


@main_bp.route('/login', methods=["GET", "POST"], endpoint='login')
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login bem-sucedido!", "auth_success")
            return redirect(url_for('main.index'))
        else:
            flash("Credenciais inválidas", "auth_danger")
    return render_template("user/login.html")


@main_bp.route('/logout', methods=['GET', 'POST'], endpoint='logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout realizado com sucesso.", "auth_success")
    return redirect(url_for('main.index'))


@main_bp.get('/api/produtos')
@require_oauth()
def api_list_products():
    return jsonify(list_products()), 200


@main_bp.get('/api/produtos/<int:id_product>')
@require_oauth()
def api_get_product(id_product: int):
    try:
        prod = product_by_id(id_product)
        return jsonify(prod), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@main_bp.post('/api/produtos')
@require_oauth()
def api_create_product():
    if not has_role("products:write"):
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(force=True, silent=True) or {}
    try:
        new_prod = create_product({
            "name": data["name"],
            "price": float(data["price"]),
            "description": data.get("description"),
        })
        return jsonify(new_prod), 201
    except KeyError as e:
        return jsonify({"error": f"Campo faltando: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.put('/api/produtos/<int:id_product>')
@require_oauth()
def api_update_product(id_product: int):
    if not has_role("products:write"):
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(force=True, silent=True) or {}
    try:
        upd = update_product(id_product, {
            "name": data["name"],
            "price": float(data["price"]),
            "description": data.get("description"),
        })
        return jsonify(upd), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except KeyError as e:
        return jsonify({"error": f"Campo faltando: {e}"}), 400


@main_bp.delete('/api/produtos/<int:id_product>')
@require_oauth()
def api_delete_product(id_product: int):
    if not has_role("products:write"):
        return jsonify({"error": "forbidden"}), 403
    try:
        delete_product(id_product)
        return "", 204
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
