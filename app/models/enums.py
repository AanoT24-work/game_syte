import enum

class SessionStatus(enum.Enum):
    """Статусы сессий - значения должны быть в нижнем регистре для PostgreSQL"""
    ACTIVE = "active"      # ← "active", а не "ACTIVE"
    EXPIRED = "expired"    # ← "expired", а не "EXPIRED"
    REVOKED = "revoked"    # ← "revoked", а не "REVOKED"
    REFRESHED = "refreshed"# ← "refreshed", а не "REFRESHED"
    
    @classmethod
    def from_string(cls, value):
        """Создать Enum из строки (регистронезависимо)"""
        if not value:
            return cls.ACTIVE
        
        value_lower = value.lower()
        for member in cls:
            if member.value == value_lower:
                return member
        
        raise ValueError(f"Invalid session status: {value}")

class UserStatus(enum.Enum):
    """Статусы пользователей"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    BANNED = "banned"