import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

def save_avatar(file):
    """
    Сохраняет аватар пользователя
    Возвращает имя файла или вызывает исключение
    """
    if not file or file.filename == '':
        raise ValueError("Файл не выбран")
    
    # Проверка расширения
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_ext not in allowed_extensions:
        raise ValueError(f"Неподдерживаемый формат: {file_ext}")
    
    # Создаем уникальное имя
    random_hex = uuid.uuid4().hex[:8]
    new_filename = f"avatar_{random_hex}.{file_ext}"
    
    # Определяем путь для сохранения
    upload_folder = os.path.join(current_app.root_path, 'static', 'upload', 'avatars')
    
    # Создаем папку если не существует
    os.makedirs(upload_folder, exist_ok=True)
    
    # Полный путь к файлу
    file_path = os.path.join(upload_folder, new_filename)
    
    try:
        # Сохраняем файл
        file.save(file_path)
        return new_filename
        
    except Exception as e:
        raise ValueError(f"Ошибка при сохранении файла: {str(e)}")