#!/usr/bin/env python3
import psycopg2
import sys
import os

def add_postgresql_fields():
    """Добавляет поля для редактирования в PostgreSQL"""
    
    # Данные из вашего .env файла
    POSTGRES_USER = 'danila'
    POSTGRES_PASSWORD = 'bmws1000rr'
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = '54322'  # Ваш порт 54322
    POSTGRES_DB = 'mydb_site2'
    
    try:
        print(f"🔗 Подключаемся к PostgreSQL...")
        print(f"   Хост: {POSTGRES_HOST}:{POSTGRES_PORT}")
        print(f"   База: {POSTGRES_DB}")
        print(f"   Пользователь: {POSTGRES_USER}")
        
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Успешно подключились к PostgreSQL!")
        
        # Проверяем существующие столбцы
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'messages'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        if not columns:
            print("⚠️ Таблица 'messages' не найдена! Создана ли она?")
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'messages'")
            tables = cursor.fetchall()
            print(f"📋 Доступные таблицы: {tables}")
            return
        
        print("\n📋 Существующие столбцы в таблице messages:")
        column_names = []
        for col in columns:
            column_names.append(col[0])
            print(f"  - {col[0]} ({col[1]})")
        
        # Проверяем и добавляем поля
        print("\n➕ Проверяем и добавляем новые поля...")
        
        # 1. is_edited
        if 'is_edited' not in column_names:
            try:
                cursor.execute("""
                    ALTER TABLE messages 
                    ADD COLUMN is_edited BOOLEAN DEFAULT FALSE;
                """)
                print("✅ Добавлено поле 'is_edited' (BOOLEAN DEFAULT FALSE)")
            except Exception as e:
                print(f"⚠️ Ошибка при добавлении is_edited: {e}")
        else:
            print("✓ Поле 'is_edited' уже существует")
        
        # 2. edited_at
        if 'edited_at' not in column_names:
            try:
                cursor.execute("""
                    ALTER TABLE messages 
                    ADD COLUMN edited_at TIMESTAMP;
                """)
                print("✅ Добавлено поле 'edited_at' (TIMESTAMP)")
            except Exception as e:
                print(f"⚠️ Ошибка при добавлении edited_at: {e}")
        else:
            print("✓ Поле 'edited_at' уже существует")
        
        # 3. edit_history
        if 'edit_history' not in column_names:
            try:
                # Пробуем добавить как JSONB (PostgreSQL 9.4+)
                cursor.execute("""
                    ALTER TABLE messages 
                    ADD COLUMN edit_history JSONB DEFAULT '[]'::jsonb;
                """)
                print("✅ Добавлено поле 'edit_history' (JSONB DEFAULT '[]')")
            except Exception as e:
                print(f"⚠️ JSONB не поддерживается: {e}")
                try:
                    # Пробуем добавить как TEXT
                    cursor.execute("""
                        ALTER TABLE messages 
                        ADD COLUMN edit_history TEXT DEFAULT '[]';
                    """)
                    print("✅ Добавлено поле 'edit_history' (TEXT DEFAULT '[]')")
                except Exception as e2:
                    print(f"⚠️ Ошибка при добавлении edit_history: {e2}")
        else:
            print("✓ Поле 'edit_history' уже существует")
        
        # Проверяем финальную структуру
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'messages'
            ORDER BY ordinal_position;
        """)
        
        print("\n🎉 Финальная структура таблицы messages:")
        for col in cursor.fetchall():
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"  - {col[0]:20} {col[1]:15} {nullable}")
        
        # Также проверяем наличие таблицы messages вообще
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        print(f"\n📊 Количество сообщений в таблице: {count}")
        
        cursor.close()
        conn.close()
        print("\n✅ Готово! Поля успешно добавлены.")
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Ошибка подключения к PostgreSQL: {e}")
        print("   Проверьте:")
        print("   1. Запущен ли PostgreSQL сервер?")
        print("   2. Правильный ли порт? (54322)")
        print("   3. Существует ли база данных 'mydb_site2'?")
        print("   4. Правильные ли логин/пароль?")
        
        # Проверяем доступность порта
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((POSTGRES_HOST, int(POSTGRES_PORT)))
        if result == 0:
            print(f"   🔍 Порт {POSTGRES_PORT} открыт")
        else:
            print(f"   🔍 Порт {POSTGRES_PORT} закрыт или недоступен")
        sock.close()
        
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_postgresql_fields()