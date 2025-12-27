# app/services/auth_service.py

from datetime import datetime
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
            # Создаём сессию с временным хэшем
            temp_token = "temp"  # временный токен для инициализации
            session = SessionRepository.create_session(
                user_id=user.id,
                refresh_token=temp_token,
                user_agent=user_agent,
                ip_address=ip_address
            )

            # Генерируем настоящий refresh-токен с session.id
            access_token, refresh_token = JWTManager.create_token_pair(user, session.id)

            # Обновляем сессию настоящим хэшем, НЕ помечая как refreshed
            SessionRepository.update_session_token(session, refresh_token, mark_refreshed=False)

            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'expires_in': JWTManager._get_default_expiry('access'),
                'user': user.to_dict()
            }, None

        except Exception as e:
            current_app.logger.error(f"Auth response error: {e}")
            return None, "Ошибка сервера"

    @staticmethod
    def refresh_tokens(refresh_token: str) -> tuple:
        """Обновить токены по refresh токену."""
        try:
            # 1. Декодируем токен
            payload = JWTManager.verify_refresh_token(refresh_token)
            if not payload:
                return None, "Недействительный токен"

            user_id = int(payload['sub'])
            session_id = payload['session_id']

            # 2. Проверяем сессию
            session = SessionRepository.find_active_session(session_id, refresh_token)
            if not session:
                return None, "Сессия не найдена или отозвана"

            # 3. Проверяем пользователя
            user = User.query.get(user_id)
            if not user:
                return None, "Пользователь не найден"

            # 4. Отзываем старую сессию
            SessionRepository.revoke_session(session_id)

            # 5. Создаём новую сессию
            new_session = SessionRepository.create_session(
                user_id=user.id,
                refresh_token="temp",
                user_agent=request.headers.get('User-Agent', 'Unknown')[:500],
                ip_address=request.remote_addr
            )

            # 6. Генерируем новые токены
            new_access, new_refresh = JWTManager.create_token_pair(user, new_session.id)

            # 7. Обновляем хэш, помечая как refreshed (это правильно для refresh)
            SessionRepository.update_session_token(new_session, new_refresh, mark_refreshed=True)

            return {
                'access_token': new_access,
                'refresh_token': new_refresh,
                'token_type': 'bearer',
                'expires_in': JWTManager._get_default_expiry('access')
            }, None

        except Exception as e:
            current_app.logger.error(f"Refresh error: {e}")
            return None, "Ошибка сервера"