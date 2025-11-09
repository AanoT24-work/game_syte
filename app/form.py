from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, SelectField, StringField, PasswordField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

from app.models.user import User

class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Подтвердить')
    

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
    
    
class AccauntForm(FlaskForm):
    # ПРАВИЛЬНО: FileField с FileAllowed как валидатор
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