import os.path
import secrets
from PIL import Image
from flask import current_app

AVATAR_SIZES = {
    'small': (125, 125),
    'medium': (250, 250), 
    'large': (500, 500)
}

POST_SIZES = {
    'thumbnail': (300, 300),
    'standard': (800, 600),
    'high_quality': (1200, 900)
}

def save_picture(picture,  image_type='avatar', size='medium'):

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
    picture_path = os.path.join(current_app.config['SERVER_PATH'], picture_fn)
    upload_folder = os.path.dirname(picture_path)
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    if image_type == 'avatar':
        output_size = AVATAR_SIZES.get(size, AVATAR_SIZES['medium'])
    else:  # post
        output_size = POST_SIZES.get(size, POST_SIZES['standard'])
    
    if i.mode in ('RGBA', 'LA', 'P'):
        i = i.convert('RGB')
    i.thumbnail(output_size, Image.Resampling.LANCZOS)
    i.save(picture_path, optimize=True, quality=95)
    
    return picture_fn