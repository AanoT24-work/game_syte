import jwt
from datetime import datetime, timedelta
from flask import current_app
from typing import Dict, Optional, Tuple

from app.models.user import User


class JWTManager:
    # Увеличена читаемость и добавлена централизованная проверка конфигурации
    @staticmethod
    def _get_secret_key(token_type: str) -> str:
        """Вернуть секретный ключ в зависимости от типа токена."""
        if token_type == 'access':
            return current_app.config['JWT_SECRET_KEY']
        elif token_type == 'refresh':
            return current_app.config['JWT_REFRESH_SECRET_KEY']
        else:
            raise ValueError(f"Unsupported token type: {token_type}")

    @staticmethod
    def _get_default_expiry(token_type: str) -> int:
        """Вернуть время жизни токена по умолчанию в зависимости от типа."""
        defaults = {
            'access': 900,   # 15 минут
            'refresh': 2592000  # 30 дней
        }
        key = f'JWT_{token_type.upper()}_TOKEN_EXPIRES'
        return current_app.config.get(key, defaults[token_type])

    @staticmethod
    def create_access_token(user_data: Dict, expires_in: Optional[int] = None) -> str:
        """Создать access токен (15 минут по умолчанию)."""
        if expires_in is None:
            expires_in = JWTManager._get_default_expiry('access')

        payload = {
            **user_data,
            'type': 'access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }

        return jwt.encode(
            payload,
            JWTManager._get_secret_key('access'),
            algorithm='HS256'
        )

    @staticmethod
    def create_refresh_token(user_id: int, session_id: int) -> str:
        """Создать refresh токен (30 дней по умолчанию)."""
        expires_in = JWTManager._get_default_expiry('refresh')

        payload = {
            'sub': str(user_id),
            'session_id': session_id,
            'type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }

        return jwt.encode(
            payload,
            JWTManager._get_secret_key('refresh'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_token(token: str, token_type: str = 'access') -> Optional[Dict]:
        """Декодировать и верифицировать токен с валидацией типа и обязательных полей."""
        try:
            secret_key = JWTManager._get_secret_key(token_type)

            # Явная проверка наличия необходимых claim'ов
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=['HS256'],
                options={
                    'require': ['exp', 'iat', 'type'],
                    'verify_exp': True,
                    'verify_iat': True
                }
            )

            # Проверка типа токена
            if payload.get('type') != token_type:
                current_app.logger.warning(
                    f"Token type mismatch: expected {token_type}, got {payload.get('type')}"
                )
                return None

            return payload

        except jwt.ExpiredSignatureError:
            current_app.logger.warning(f"{token_type.upper()} token expired")
            return None
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Invalid {token_type} token: {e}")
            return None
        except Exception as e:
            current_app.logger.error(f"Unexpected error during token decoding: {e}")
            return None

    @staticmethod
    def create_token_pair(user: User, session_id: int) -> Tuple[str, str]:
        """Создать пару токенов: access и refresh."""
        access_token = JWTManager.create_access_token({
            'sub': str(user.id),
            'login': user.login,
            'avatar': user.avatar,
            'status': user.status
        })

        refresh_token = JWTManager.create_refresh_token(user.id, session_id)

        return access_token, refresh_token

    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict]:
        """Проверить access токен."""
        return JWTManager.decode_token(token, 'access')

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict]:
        """Проверить refresh токен."""
        return JWTManager.decode_token(token, 'refresh')
