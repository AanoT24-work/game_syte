from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return jsonify({'error': 'Требуются логин и пароль'}), 400

    user_obj, error = AuthService.authenticate(login, password)
    if error:
        return jsonify({'error': error}), 401

    response, error = AuthService.create_auth_response(user_obj)
    if error:
        return jsonify({'error': error}), 500

    return jsonify(response), 200


@auth_bp.route('/auth/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'error': 'Требуется refresh токен'}), 400

    tokens, error = AuthService.refresh_tokens(refresh_token)
    if error:
        return jsonify({'error': error}), 401

    return jsonify(tokens), 200