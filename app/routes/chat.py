from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for, jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
import os
from sqlalchemy import or_
from datetime import datetime, timedelta

from app import form
from app.functions import save_picture
from ..extensions import db
from ..models.user import User
from ..models.post import Message

chat = Blueprint('chat', __name__)

@chat.route('/chat/messenger')
@login_required
def messenger():
    return render_template('post/messenger.html', form=form)

@chat.route('/search_users')
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    users = User.query.filter(
        User.login.ilike(f'%{query}%'),
        User.id != current_user.id
    ).limit(10).all()
    
    results = []
    for user in users:
        # Проверяем есть ли чат
        existing_chat = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user.id)) |
            ((Message.sender_id == user.id) & (Message.receiver_id == current_user.id))
        ).first()
        
        results.append({
            'id': user.id,
            'username': user.login,
            'avatar': user.avatar or 'default_avatar.png',  # Гарантируем что будет значение
            'has_chat': existing_chat is not None
        })
    
    return jsonify(results)

@chat.route('/start_chat/<int:user_id>')
@login_required
def start_chat(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Нельзя начать чат с самим собой'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    # Проверяем есть ли уже чат
    existing_chat = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).first()
    
    if existing_chat:
        return jsonify({'chat_exists': True, 'chat_id': user_id})
    
    # Создаем первое сообщение
    new_message = Message(
        text=f"Привет! Чат начат 👋",
        sender_id=current_user.id,
        receiver_id=user_id
    )
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({'success': True, 'chat_id': user_id})

@chat.route('/get_chats')
@login_required
def get_chats():
    """Получаем список всех чатов пользователя"""
    # Находим всех пользователей, с которыми есть переписка
    sent_chats = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user.id).distinct()
    received_chats = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user.id).distinct()
    
    all_chat_user_ids = set([id[0] for id in sent_chats] + [id[0] for id in received_chats])
    
    chats = []
    for user_id in all_chat_user_ids:
        user = User.query.get(user_id)
        if not user:
            continue
            
        # Получаем последнее сообщение в чате
        last_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.created_at.desc()).first()
        
        # Считаем непрочитанные сообщения
        unread_count = Message.query.filter(
            Message.sender_id == user_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).count()
        
        chats.append({
            'user_id': user.id,
            'username': user.login,
            'avatar': user.avatar or 'default_avatar.png',
            'last_message': last_message.text if last_message else '',
            'last_message_time': last_message.created_at.isoformat() if last_message else '',
            'unread_count': unread_count
        })
    
    # Сортируем по времени последнего сообщения
    chats.sort(key=lambda x: x['last_message_time'] or '', reverse=True)
    
    return jsonify(chats)

@chat.route('/get_messages/<int:user_id>')
@login_required
def get_messages(user_id):
    """Получаем сообщения с конкретным пользователем"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    # Помечаем сообщения как прочитанные
    Message.query.filter(
        Message.sender_id == user_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).update({'is_read': True, 'read_at': datetime.utcnow()})
    db.session.commit()
    
    # Получаем все сообщения
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Форматируем сообщения
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'text': msg.text,
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'created_at': msg.created_at.isoformat() if msg.created_at else '',
            'is_read': msg.is_read,
            'is_edited': msg.is_edited,  # Добавляем поле
            'edited_at': msg.edited_at.isoformat() if msg.edited_at else None  # Добавляем поле
        })
    
    return jsonify({
        'user': {
            'id': user.id, 
            'username': user.login,
            'avatar': user.avatar or 'default_avatar.png'
        },
        'messages': messages_data
    })

@chat.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Отправка нового сообщения"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        receiver_id = data.get('receiver_id')
        text = data.get('text', '').strip()
        
        if not receiver_id:
            return jsonify({'error': 'Не указан получатель'}), 400
            
        if not text:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
        # Преобразуем receiver_id в int
        try:
            receiver_id = int(receiver_id)
        except (ValueError, TypeError):
            return jsonify({'error': 'Неверный формат ID получателя'}), 400
        
        if receiver_id == current_user.id:
            return jsonify({'error': 'Нельзя отправить сообщение самому себе'}), 400
        
        user = User.query.get(receiver_id)
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        new_message = Message(
            text=text,
            sender_id=current_user.id,
            receiver_id=receiver_id
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"ERROR in send_message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

@chat.route('/get_unread_count')
@login_required
def get_unread_count():
    """Получаем количество непрочитанных сообщений"""
    count = Message.query.filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return jsonify({'unread_count': count})

@chat.route('/delete_message/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Удаление сообщения"""
    try:
        message = Message.query.get(message_id)
        
        if not message:
            return jsonify({'error': 'Сообщение не найдено'}), 404
        
        # Проверяем что пользователь является отправителем сообщения
        if message.sender_id != current_user.id:
            return jsonify({'error': 'Можно удалять только свои сообщения'}), 403
        
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Сообщение удалено'})
        
    except Exception as e:
        print(f"Error deleting message: {e}")
        return jsonify({'error': str(e)}), 500

@chat.route('/clear_chat/<int:user_id>', methods=['DELETE'])
@login_required
def clear_chat(user_id):
    """Очистка всей переписки с пользователем"""
    try:
        # Удаляем сообщения в обе стороны (или только свои - в зависимости от требований)
        deleted_count = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
            ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Удалено {deleted_count} сообщений',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"Error clearing chat: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@chat.route('/user/avatar/<int:user_id>')
@login_required
def get_user_avatar(user_id):
    """Получение аватарки пользователя"""
    try:
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User {user_id} not found")
            # Возвращаем аватарку по умолчанию
            return send_from_directory('static', 'images/default_avatar.png')
        
        print(f"🔍 AVATAR REQUEST - User: {user.id}, Avatar filename: {user.avatar}")
        
        # Если аватарки нет или дефолтная
        if not user.avatar or user.avatar == 'default_avatar.png':
            print("ℹ️ Using default avatar")
            return send_from_directory('static', 'images/default_avatar.png')
        
        # Пробуем найти файл аватарки
        avatar_filename = user.avatar
        
        # Пробуем разные возможные пути
        possible_paths = [
            os.path.join(current_app.root_path, 'static', 'avatars', avatar_filename),
            os.path.join(current_app.root_path, 'static', 'uploads', 'avatars', avatar_filename),
            os.path.join(current_app.root_path, 'static', 'images', avatar_filename),
            os.path.join(current_app.root_path, 'static', 'upload', avatar_filename),
        ]
        
        for avatar_path in possible_paths:
            print(f"🔍 Checking path: {avatar_path}")
            if os.path.exists(avatar_path):
                print(f"✅ Avatar found: {avatar_path}")
                return send_file(avatar_path)
        
        print(f"❌ Avatar file not found: {avatar_filename}")
        return send_from_directory('static', 'images/default_avatar.png')
        
    except Exception as e:
        print(f"💥 Avatar error: {str(e)}")
        import traceback
        traceback.print_exc()
        return send_from_directory('static', 'images/default_avatar.png')

@chat.route('/edit_message/<int:message_id>', methods=['PUT'])
@login_required
def edit_message(message_id):
    """Редактирование сообщения"""
    try:
        data = request.get_json()
        print(f"📝 EDIT REQUEST - Message ID: {message_id}, Data: {data}")  # Отладка
        
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        new_text = data.get('text', '').strip()
        if not new_text:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
        # Получаем сообщение
        message = Message.query.get(message_id)
        if not message:
            print(f"❌ Message {message_id} not found")
            return jsonify({'error': 'Сообщение не найдено'}), 404
        
        print(f"🔍 FOUND MESSAGE - ID: {message.id}, Sender: {message.sender_id}, Current User: {current_user.id}")
        
        # Проверяем права на редактирование
        if message.sender_id != current_user.id:
            print(f"❌ Permission denied - sender: {message.sender_id}, current user: {current_user.id}")
            return jsonify({'error': 'Можно редактировать только свои сообщения'}), 403
        
        # Проверяем временное ограничение (15 минут)
        time_limit = datetime.utcnow() - timedelta(minutes=15)
        if message.created_at < time_limit:
            print(f"⏰ Message too old to edit - created: {message.created_at}, limit: {time_limit}")
            return jsonify({'error': 'Сообщение можно редактировать только в течение 15 минут'}), 400
        
        # Сохраняем старый текст для истории
        old_text = message.text
        
        print(f"📝 EDITING - Old text: '{old_text}', New text: '{new_text}'")
        
        # Обновляем сообщение
        message.text = new_text
        message.is_edited = True
        message.edited_at = datetime.utcnow()
        
        # Добавляем в историю (если метод существует)
        if hasattr(message, 'add_edit_history'):
            message.add_edit_history(old_text)
        else:
            # Если метода нет, просто устанавливаем флаг
            print("⚠️ add_edit_history method not available")
        
        db.session.commit()
        
        print(f"✅ Message {message_id} edited successfully")
        
        return jsonify({
            'success': True,
            'message': 'Сообщение обновлено',
            'edited_at': message.edited_at.isoformat(),
            'text': message.text,
            'created_at': message.created_at.isoformat()  # Добавляем created_at для обновления времени
        })
        
    except Exception as e:
        print(f"❌ Error editing message: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@chat.route('/get_message_history/<int:message_id>')
@login_required
def get_message_history(message_id):
    """Получение истории редактирования сообщения"""
    try:
        print(f"📜 Getting history for message {message_id}")
        
        message = Message.query.get(message_id)
        if not message:
            print(f"❌ Message {message_id} not found")
            return jsonify({'error': 'Сообщение не найдено'}), 404
        
        # Проверяем права (только участники чата)
        if message.sender_id != current_user.id and message.receiver_id != current_user.id:
            print(f"❌ Access denied for user {current_user.id}")
            return jsonify({'error': 'Нет доступа к истории'}), 403
        
        # Получаем историю
        history = []
        if hasattr(message, 'get_edit_history'):
            history = message.get_edit_history()
        elif message.edit_history:
            # Пробуем распарсить JSON вручную
            try:
                import json
                history = json.loads(message.edit_history)
            except:
                history = []
        
        print(f"📜 History retrieved: {len(history)} items")
        
        return jsonify({
            'success': True,
            'history': history,
            'is_edited': message.is_edited,
            'edited_at': message.edited_at.isoformat() if message.edited_at else None
        })
        
    except Exception as e:
        print(f"❌ Error getting message history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
