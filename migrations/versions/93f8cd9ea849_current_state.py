"""Current database state

Revision ID: 93f8cd9ea849
Revises: 
Create Date: 2024-01-15 10:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = '93f8cd9ea849'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Таблицы уже созданы вручную, ничего не делаем
    pass

def downgrade():
    # Не удаляем таблицы чтобы не потерять данные
    pass
