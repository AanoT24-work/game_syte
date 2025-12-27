from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.decorators import jwt_required, get_jwt_identity  # Импортируйте
from app.models.user import User

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


# ДОБАВЬТЕ ЭТОТ ЭНДПОИНТ!
@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required
def get_current_user():
    """Получить информацию о текущем пользователе (защищенный эндпоинт)."""
    payload = get_jwt_identity()
    
    if not payload:
        return jsonify({'error': 'Неавторизован'}), 401
    
    user_id = int(payload.get('sub'))
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    return jsonify({
        'user': user.to_dict(),
        'session_id': payload.get('session_id'),
        'message': 'Доступ разрешен'
    }), 200