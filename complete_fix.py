# complete_fix.py
import sys
import os

# Установи ТВОИ реальные данные
os.environ['POSTGRES_USER'] = 'danila'
os.environ['POSTGRES_PASSWORD'] = 'bmws1000rr'
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '54322'  # ← 54322!
os.environ['POSTGRES_DB'] = 'mydb_site2'
os.environ['KEY'] = 'asb5142hvkjsafv9234r32kjasfilaweurfa'

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def main():
    print("🚀 Начинаем полный сброс БД и миграций...")
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️  Удаляем таблицы из БД...")
            db.drop_all()
            print("✅ Все таблицы удалены из БД")
            
            import shutil
            if os.path.exists('migrations'):
                shutil.rmtree('migrations')
                print("✅ Папка migrations удалена")
            
            print("🔧 Создаем таблицы...")
            db.create_all()
            print("✅ Таблицы созданы напрямую")
            
            print("\n🎉 ВСЕ ГОТОВО! База данных полностью пересоздана!")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())