from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.session import UserSession

app = create_app()
with app.app_context():
    # Найти пользователя
    user = User.query.filter_by(login='danila11').first()
    print(f"Пользователь: {user.login}, ID: {user.id}")
    
    # Проверить сессии
    sessions = UserSession.query.filter_by(user_id=user.id).all()
    print(f"Количество сессий: {len(sessions)}")
    for s in sessions:
        print(f"  ID: {s.id}, Status: {s.status}, Created: {s.created_at}")
    
    # Удалить все сессии
    deleted = UserSession.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    print(f"Удалено сессий: {deleted}")
