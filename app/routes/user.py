from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, current_app
from flask_login import current_user, login_user, logout_user
import os
from sqlalchemy.exc import IntegrityError

from app.functions import save_picture  # ← ИСПОЛЬЗУЙ СУЩЕСТВУЮЩУЮ ФУНКЦИЮ!
from app.models import post

from ..extensions import db, bcrypt
from ..form import AccauntForm, LoginForm, RegistrationForm
from ..models.user import User

user = Blueprint('user', __name__)



@user.route('/user/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    
    if current_user.is_authenticated:
        flash("Вы уже авторизованы", "success")
        return redirect(url_for('post.all'))
    
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
            return redirect(url_for('post.all'))
        
        except Exception as e:
            db.session.rollback()
            print(f'Ошибка регистрации: {str(e)}')
            flash('При регистрации возникла ошибка', 'danger')
    
    return render_template('user/register.html', form=form)


@user.route('/user/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            try:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                flash(f'Поздравляю {form.login.data} вы успешно авторизовались', "success")
                return redirect(next_page) if next_page else redirect(url_for('post.all'))
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


@user.route('/user/accaunt', methods=['POST', 'GET'])
def accaunt():
    form = AccauntForm()
    
    if form.validate_on_submit():
        try:
            if form.avatar.data:
                # ИСПОЛЬЗУЙ save_picture вместо save_avatar
                avatar_filename = save_picture(form.avatar.data, image_type='avatar')
                current_user.avatar = avatar_filename
                db.session.commit()
                flash('Аватар успешно обновлен!', 'success')
                return redirect(url_for('user.accaunt'))
                
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при загрузке аватара: {str(e)}", "danger")
    
    return render_template('user/accaunt.html', form=form)


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
        
        # ИСПОЛЬЗУЙ save_picture вместо save_avatar
        avatar_filename = save_picture(file, image_type='avatar')
        
        # Обновляем пользователя
        current_user.avatar = avatar_filename
        db.session.commit()
        
        # Возвращаем URL нового аватара
        avatar_url = url_for('static', filename=f'upload/avatars/{avatar_filename}')
        
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
        if current_user.avatar and current_user.avatar != 'default_avatar.png':
            avatar_path = os.path.join(
                current_app.root_path, 
                'static', 'upload', 'avatars', 
                current_user.avatar
            )
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        
        # Устанавливаем аватар по умолчанию
        current_user.avatar = 'default_avatar.png'
        db.session.commit()
        
        # URL дефолтного аватара
        default_avatar_url = url_for('static', filename='upload/avatars/default_avatar.png')
        
        return jsonify({
            'success': True,
            'avatar_url': default_avatar_url,
            'message': 'Аватар удален'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})