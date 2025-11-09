from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, current_app, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required  # Добавьте login_required
import os
from sqlalchemy.exc import IntegrityError

from app.functions import save_picture
from ..models.post import Post

from ..extensions import db, bcrypt
from ..form import AccauntForm, LoginForm, RegistrationForm, PostForm
from ..models.user import User

user = Blueprint('user', __name__)

# Вспомогательная функция для проверки, является ли аватар дефолтным
def is_default_avatar(avatar_filename):
    return avatar_filename in [None, '', 'default_avatar.png']

@user.route('/user/support')
def support():
    return render_template('user/support.html')

@user.route('/user/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    
    if current_user.is_authenticated:
        flash("Вы уже авторизованы", "success")
        return redirect(url_for('post.all_posts'))  # ИСПРАВИЛ
    
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter_by(login=form.login.data).first()
            if existing_user:
                flash('Пользователь с таким именем уже существует', 'danger')
                return render_template('user/register.html', form=form)
            
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(login=form.login.data, password=hashed_password)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user, remember=True)
            flash(f'Поздравляем {form.login.data}! Вы успешно зарегистрированы и авторизованы', 'success')
            return redirect(url_for('post.all_posts'))  # ИСПРАВИЛ
        
        except Exception as e:
            db.session.rollback()
            print(f'Ошибка регистрации: {str(e)}')
            flash('При регистрации возникла ошибка', 'danger')
    
    return render_template('user/register.html', form=form)

@user.route('/user/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    
    if current_user.is_authenticated:
        return redirect(url_for('post.all_posts'))  # ИСПРАВИЛ
    
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            try:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                flash(f'Поздравляю {form.login.data} вы успешно авторизовались', "success")
                return redirect(next_page) if next_page else redirect(url_for('post.all_posts'))  # ИСПРАВИЛ
            except Exception as e:
                print(f'Ошибка входа: {str(e)}')
                flash('Ошибка входа! Попробуйте еще раз', "danger")
        else:
            flash('Неверный логин или пароль', "danger")
            
    return render_template('user/login.html', form=form)

@user.route('/user/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@user.route('/user/accaunt')
@login_required
def accaunt():
    """Страница собственного аккаунта - перенаправление на профиль"""
    return redirect(url_for('user.profile', user_id=current_user.id))

@user.route('/user/<int:user_id>')
def profile(user_id):
    """Страница профиля любого пользователя"""
    user = User.query.get_or_404(user_id)
    accaunt_form = AccauntForm()
    post_form = PostForm()
    
    # Получаем посты пользователя
    user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    
    return render_template('user/accaunt.html', 
                         user=user,
                         accaunt_form=accaunt_form, 
                         post_form=post_form,
                         posts=user_posts)

@user.route('/avatar/<int:user_id>')
def get_avatar(user_id):
    """Просмотр аватара любого пользователя"""
    user = User.query.get_or_404(user_id)
    
    # Проверяем существование файла аватара и не является ли он дефолтным
    if user.avatar and not is_default_avatar(user.avatar):
        avatar_path = os.path.join(current_app.root_path, 'static', 'upload', 'avatars', user.avatar)
        if os.path.exists(avatar_path):
            return send_from_directory(
                os.path.join(current_app.root_path, 'static', 'upload', 'avatars'),
                user.avatar
            )
    
    # Возвращаем аватар по умолчанию
    return send_from_directory(
        os.path.join(current_app.root_path, 'static', 'upload', 'avatars'),
        'default_avatar.png'
    )

# AJAX ЭНДПОИНТЫ ДЛЯ JavaScript

@user.route('/upload-avatar', methods=['POST'])
def upload_avatar_ajax():
    """API endpoint для загрузки аватара через AJAX"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Не авторизован'})
    
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'Файл не выбран'})
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Файл не выбран'})
        
        avatar_filename = save_picture(file, image_type='avatar')
        
        # Обновляем пользователя
        current_user.avatar = avatar_filename
        db.session.commit()
        
        # Возвращаем URL нового аватара
        avatar_url = url_for('user.get_avatar', user_id=current_user.id)
        
        return jsonify({
            'success': True, 
            'avatar_url': avatar_url,
            'message': 'Аватар успешно обновлен'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@user.route('/delete-avatar', methods=['POST'])
def delete_avatar_ajax():
    """API endpoint для удаления аватара через AJAX"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Не авторизован'})
    
    try:
        # Удаляем старый файл аватара (если он не дефолтный)
        if current_user.avatar and not is_default_avatar(current_user.avatar):
            avatar_path = os.path.join(
                current_app.root_path, 
                'static', 'upload', 'avatars', 
                current_user.avatar
            )
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        
        # Устанавливаем аватар как None вместо 'default_avatar.png'
        current_user.avatar = None
        db.session.commit()
        
        # URL дефолтного аватара
        default_avatar_url = url_for('user.get_avatar', user_id=current_user.id)
        
        return jsonify({
            'success': True,
            'avatar_url': default_avatar_url,
            'message': 'Аватар удален'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})