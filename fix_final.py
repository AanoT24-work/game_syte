from app import create_app
from app.extensions import db
from app.models.session import UserSession, SessionStatus
from app.models.user import User

app = create_app()
with app.app_context():
    # 1. Проверим метод update_session_token
    print("=== ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ ===")
    user = User.query.filter_by(login='demo_user').first()
    sessions = UserSession.query.filter_by(user_id=user.id).all()
    
    for s in sessions:
        print(f"ID: {s.id}, Status: {s.status}, Active: {s.is_active()}")
    
    # 2. Исправим последнюю сессию
    last_session = sessions[-1] if sessions else None
    if last_session and last_session.status == SessionStatus.REFRESHED:
        print(f"\n=== ИСПРАВЛЕНИЕ ===")
        print(f"Было: ID={last_session.id}, Status={last_session.status}")
        last_session.status = SessionStatus.ACTIVE
        db.session.commit()
        print(f"Стало: ID={last_session.id}, Status={last_session.status}")
    
    # 3. Проверим исправление
    print(f"\n=== ПРОВЕРКА ПОСЛЕ ИСПРАВЛЕНИЯ ===")
    sessions_after = UserSession.query.filter_by(user_id=user.id).all()
    for s in sessions_after:
        active = "✓" if s.is_active() else "✗"
        print(f"ID: {s.id}, Status: {s.status} {active}")
