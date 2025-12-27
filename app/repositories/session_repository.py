from datetime import datetime, timedelta
from typing import Optional
from app.models.enums import SessionStatus
from app.models.session import UserSession
from app.extensions import db


class SessionRepository:
    @staticmethod
    def create_session(user_id: int, refresh_token: str,
                      user_agent: str = None, ip_address: str = None,
                      expires_in_days: int = 30) -> UserSession:
        """Создать новую сессию."""
        token_hash = UserSession.hash_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        session = UserSession(
            user_id=user_id,
            refresh_token_hash=token_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )

        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def find_active_session(session_id: int, refresh_token: str) -> Optional[UserSession]:
        """Найти активную сессию по ID и сырому токену."""
        if not session_id or not refresh_token:
            return None

        token_hash = UserSession.hash_token(refresh_token)
        session = db.session.get(UserSession, session_id)
        if not session:
            return None

        # Проверяем хэш и активность
        if session.refresh_token_hash != token_hash:
            return None
        if not session.is_active():
            return None

        session.update_last_used()
        db.session.commit()
        return session

    @staticmethod
    def find_active_by_id(session_id: int) -> Optional[UserSession]:
        """Найти активную сессию только по ID (без проверки токена)."""
        if not session_id:
            return None
            
        session = db.session.get(UserSession, session_id)
        if not session:
            return None
            
        # Проверяем активность
        if not session.is_active():
            return None
            
        session.update_last_used()
        db.session.commit()
        return session

    @staticmethod
    def find_by_refresh_token_hash(token_hash: str) -> Optional[UserSession]:
        """Найти сессию по хэшу refresh токена."""
        return UserSession.query.filter_by(refresh_token_hash=token_hash).first()

    @staticmethod
    def revoke_session(session_id: int) -> bool:
        """Отозвать сессию."""
        session = db.session.get(UserSession, session_id)
        if session:
            session.revoke()
            db.session.commit()
            return True
        return False

    @staticmethod
    def update_session_token(session: UserSession, new_refresh_token: str, mark_refreshed: bool = True) -> None:
        """Обновить токен сессии."""
        new_hash = UserSession.hash_token(new_refresh_token)
        session.refresh_token_hash = new_hash
        
        if mark_refreshed:
            session.mark_as_refreshed()
        else:
            db.session.add(session)
        
        db.session.commit()

    @staticmethod
    def get_user_sessions(user_id: int) -> list:
        """Получить все сессии пользователя."""
        return UserSession.query.filter_by(user_id=user_id)\
            .order_by(UserSession.created_at.desc()).all()

    @staticmethod
    def revoke_all_user_sessions(user_id: int, exclude_session_id: int = None) -> int:
        """Отозвать все активные сессии пользователя, кроме указанной."""
        query = UserSession.query.filter_by(user_id=user_id, status=SessionStatus.ACTIVE)
        if exclude_session_id:
            query = query.filter(UserSession.id != exclude_session_id)

        count = 0
        for session in query:
            session.revoke()
            count += 1

        if count > 0:
            db.session.commit()
        return count

    @staticmethod
    def cleanup_expired() -> int:
        """Очистка истекших сессий."""
        now = datetime.utcnow()
        expired = UserSession.query.filter(
            UserSession.expires_at < now,
            UserSession.status == SessionStatus.ACTIVE
        ).all()

        count = 0
        for session in expired:
            session.status = SessionStatus.EXPIRED
            db.session.add(session)
            count += 1

        if count > 0:
            db.session.commit()
        return count