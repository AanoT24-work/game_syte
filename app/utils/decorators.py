from functools import wraps
from flask import request, jsonify, current_app
from app.utils.jwt_manager import JWTManager


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Требуется Authorization заголовок с Bearer токеном'}), 401
        
        token = auth_header.split(' ')[1]
        payload = JWTManager.verify_access_token(token)
        
        if not payload:
            return jsonify({'error': 'Недействительный или истекший токен'}), 401
        
        # Сохраняем payload в request для использования в контроллере
        request.user_payload = payload
        return f(*args, **kwargs)
    
    return decorated_function


def get_jwt_identity():
    """Получить данные из JWT токена."""
    return getattr(request, 'user_payload', None)