# app/services/auth_service.py

import secrets
from flask import current_app, request
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.utils.jwt_manager import JWTManager


class AuthService:

    @staticmethod
    def authenticate(login: str, password: str):
        """Аутентификация пользователя."""
        user = User.query.filter_by(login=login).first()
        if not user or not user.check_password(password):
            return None, "Неверный логин или пароль"
        return user, None

    @staticmethod
    def create_auth_response(user) -> tuple:
        """Создать пару токенов и сессию."""
        user_agent = request.headers.get('User-Agent', 'Unknown')[:500]
        ip_address = request.remote_addr

        try:
            # 1. Генерируем сырой токен для БД (не JWT!)
            raw_refresh_token = secrets.token_urlsafe(64)
            
            # 2. Создаём сессию в БД с сырым токеном
            session = SessionRepository.create_session(
                user_id=user.id,
                refresh_token=raw_refresh_token,  # Сырой токен для хэширования
                user_agent=user_agent,
                ip_address=ip_address
            )

            # 3. Создаем JWT токены для клиента
            # Access token с session_id
            access_token = JWTManager.create_access_token({
                'sub': str(user.id),
                'login': user.login,
                'avatar': user.avatar,
                'status': user.status,
                'session_id': session.id  # Важно для привязки!
            })
            
            # Refresh token JWT
            refresh_token_jwt = JWTManager.create_refresh_token(user.id, session.id)

            return {
                'access_token': access_token,
                'refresh_token': refresh_token_jwt,  # Клиенту отдаем JWT
                'token_type': 'bearer',
                'expires_in': current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 900),
                'user': user.to_dict()
            }, None

        except Exception as e:
            current_app.logger.error(f"Auth response error: {e}")
            return None, "Ошибка сервера"

    @staticmethod
    def refresh_tokens(refresh_token_jwt: str) -> tuple:
        """Обновить токены по refresh токену."""
        try:
            # 1. Проверяем JWT refresh токен
            payload = JWTManager.verify_refresh_token(refresh_token_jwt)
            if not payload:
                return None, "Недействительный или истекший токен"

            user_id = int(payload['sub'])
            session_id = payload['session_id']

            # 2. Находим сессию по ID (без проверки токена через find_active_by_id)
            session = SessionRepository.find_active_by_id(session_id)
            if not session:
                return None, "Сессия не найдена или неактивна"
                
            # 3. Проверяем, что сессия принадлежит пользователю
            if session.user_id != user_id:
                return None, "Несоответствие сессии и пользователя"

            # 4. Помечаем старую сессию как REFRESHED
            session.mark_as_refreshed()
            
            # 5. Создаём новую сессию с новым сырым токеном
            new_raw_refresh_token = secrets.token_urlsafe(64)
            new_session = SessionRepository.create_session(
                user_id=user_id,
                refresh_token=new_raw_refresh_token,
                user_agent=request.headers.get('User-Agent', 'Unknown')[:500],
                ip_address=request.remote_addr
            )

            # 6. Генерируем новые JWT токены
            user = User.query.get(user_id)
            if not user:
                return None, "Пользователь не найден"
                
            # Новый access token с новым session_id
            new_access_token = JWTManager.create_access_token({
                'sub': str(user.id),
                'login': user.login,
                'avatar': user.avatar,
                'status': user.status,
                'session_id': new_session.id
            })
            
            # Новый refresh token JWT
            new_refresh_token_jwt = JWTManager.create_refresh_token(user_id, new_session.id)

            return {
                'access_token': new_access_token,
                'refresh_token': new_refresh_token_jwt,
                'token_type': 'bearer',
                'expires_in': current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 900)
            }, None

        except Exception as e:
            current_app.logger.error(f"Refresh error: {e}")
            return None, "Ошибка сервера"