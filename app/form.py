import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, SelectField, StringField, PasswordField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

from app.models.user import User

class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8, max=50)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Подтвердить')
    def validate_password(self, password):
        """Кастомный валидатор для проверки сложности пароля"""
        pwd = password.data
        
        # Проверка на наличие цифр
        if not re.search(r'\d', pwd):
            raise ValidationError('Пароль должен содержать хотя бы одну цифру')
        
        # Проверка на наличие букв в верхнем регистре
        if not re.search(r'[A-ZА-Я]', pwd):
            raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
        
        # Проверка на наличие букв в нижнем регистре
        if not re.search(r'[a-zа-я]', pwd):
            raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')
        
        # Проверка на специальные символы
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise ValidationError('Пароль должен содержать хотя бы один специальный символ')
        
        # Проверка на распространенные слабые пароли
        weak_passwords = ['password', '12345678', 'qwerty', 'admin']
        if pwd.lower() in weak_passwords:
            raise ValidationError('Этот пароль слишком распространен, выберите другой')
    

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
    
    
class AccauntForm(FlaskForm):

    avatar = FileField('Аватар', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Только JPEG, JPG и PNG файлы!')])
    push = SubmitField('Сохранить')
    deleate = SubmitField('Удалить')


# НОВАЯ ФОРМА ДЛЯ ПОСТОВ
class PostForm(FlaskForm):
    content = TextAreaField('Текст поста', validators=[DataRequired(), Length(min=1, max=1000)])
    image = FileField('Изображение', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!')])
    submit = SubmitField('Сохранить')
    
class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Отправить')