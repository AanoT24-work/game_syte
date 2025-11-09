import os
import secrets
from PIL import Image
from flask import current_app

def save_picture(picture, image_type='avatar', size='large'):
    """Универсальная функция для сохранения изображений с сохранением пропорций"""
    if not picture or picture.filename == '':
        raise ValueError("Файл не был загружен")
    
    # Валидация изображения
    try:
        i = Image.open(picture)
        i.verify()
        i = Image.open(picture)  # переоткрываем после verify
    except Exception as e:
        raise ValueError(f"Файл не является изображением: {str(e)}")
    
    # Генерация имени
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    if f_ext.lower() not in allowed_extensions:
        raise ValueError(f"Неподдерживаемый формат: {f_ext}")
    
    picture_fn = random_hex + f_ext
    
    # Определяем папку и максимальные размеры
    if image_type == 'avatar':
        upload_folder = os.path.join(current_app.root_path, 'static', 'upload', 'avatars')
        max_size = (250, 250)  # Для аватаров сохраняем квадрат
        crop_to_square = True
    elif image_type == 'post':
        upload_folder = os.path.join(current_app.root_path, 'static', 'upload', 'posts')
        max_size = (2400, 1600)  # Максимальные размеры для постов
        crop_to_square = False  # Для постов сохраняем пропорции
    else:
        raise ValueError(f"Неизвестный тип изображения: {image_type}")
    
    # Создаем папку если не существует
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Сохраняем
    picture_path = os.path.join(upload_folder, picture_fn)
    
    if i.mode in ('RGBA', 'LA', 'P'):
        i = i.convert('RGB')
    
    if crop_to_square:
        # Для аватаров - обрезаем до квадрата
        i.thumbnail(max_size, Image.Resampling.LANCZOS)
    else:
        # Для постов - сохраняем пропорции
        i.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    i.save(picture_path, optimize=True, quality=85)
    
    return picture_fn