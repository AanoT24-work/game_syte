# Временное исправление для теста
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.session import UserSession, SessionStatus
import hashlib

app = create_app()
with app.app_context():
    user = User.query.filter_by(login='testuser').first()
    
    # Найдем последнюю сессию и исправим статус
    session = UserSession.query.filter_by(user_id=user.id).order_by(UserSession.created_at.desc()).first()
    
    if session and session.status == SessionStatus.REFRESHED:
        print(f"Было: ID={session.id}, Status={session.status}")
        session.status = SessionStatus.ACTIVE
        db.session.commit()
        print(f"Стало: ID={session.id}, Status={session.status}")
        print("Теперь refresh должен сработать!")
    else:
        print(f"Сессия: ID={session.id if session else 'None'}, Status={session.status if session else 'None'}")
