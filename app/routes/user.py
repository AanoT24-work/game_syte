from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user
from sqlalchemy.exc import IntegrityError

from app.models import post

from ..extensions import db, bcrypt
from ..form import LoginForm, RegistrationForm
from ..models.user import User

user = Blueprint('user', __name__)

@user.route('/user/register', methods=['POST', 'GET'])
def register():
    
    form = RegistrationForm()
    
    
    # УСЛОВИЕ ЧТОБЫ ПОСЛЕ РЕГИСТРАЦИИ АВТОМАТИЧЕСКИ ПЕРЕХОДИТЬ НА ГЛАВНУЮ СТРАНИЦУ, А НЕ НА ФОРМУ ВХОДА
    # if current_user.is_authenticated:
    #     flash("Поздравляю, вы успешно зарегистрировались", "success")
    #     return redirect(url_for('post.all'))
        
    
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
            flash(f'Поздравляем {form.login.data}! Вы успешно зарегистрированы', 'success')
            return redirect(url_for('user.login')) 
        
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