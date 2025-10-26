import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

AVATAR_SIZES = {
    'medium': (250, 250), 
    'large': (500, 500)
}

def save_picture(picture, image_type='avatar', size='medium'):
    if not picture or picture.filename == '':
        raise ValueError("Файл не был загружен")
    
    try:
        i = Image.open(picture)
        i.verify()
    except Exception as e:
        raise ValueError(f"Файл не является изображением: {str(e)}")
    
    i = Image.open(picture)
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    if f_ext.lower() not in allowed_extensions:
        raise ValueError(f"Неподдерживаемый формат: {f_ext}")
    
    picture_fn = random_hex + f_ext
    
    # ИСПРАВЛЕНИЕ: правильный путь для аватаров
    if image_type == 'avatar':
        upload_folder = os.path.join(current_app.root_path, 'static', 'upload', 'avatars')
    else:  # post
        upload_folder = os.path.join(current_app.root_path, 'static', 'upload', 'posts')
    
    # Создаем папку если не существует
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    picture_path = os.path.join(upload_folder, picture_fn)
    
    # Обработка изображения
    if image_type == 'avatar':
        output_size = AVATAR_SIZES.get(size, AVATAR_SIZES['medium'])
    else:
        output_size = (800, 600)  # для постов
    
    if i.mode in ('RGBA', 'LA', 'P'):
        i = i.convert('RGB')
    
    i.thumbnail(output_size, Image.Resampling.LANCZOS)
    i.save(picture_path, optimize=True, quality=95)
    
    return picture_fn