# Импорт необходимых компонентов Flask-WTF для работы с формами
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import BooleanField, SelectField, StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo

# Импорт модели пользователя для проверок
from app.models.user import User

# Класс формы для регистрации новых пользователей
class RegistrationForm(FlaskForm):
    # Поле для логина с валидаторами:
    # - DataRequired() - поле обязательно для заполнения
    # - Length(min=2, max=20) - длина от 2 до 20 символов
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    
    # Поле для пароля (скрытое при вводе)
    password = PasswordField('Пароль', validators=[DataRequired()])
    
    # Поле для подтверждения пароля с дополнительной проверкой совпадения
    # EqualTo('password') - проверяет, что значение совпадает с полем 'password'
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    
    # Кнопка отправки формы
    submit = SubmitField('Подтвердить')
    
    # Кастомный валидатор для проверки уникальности логина
    def validate_login(self, field):
        # Ищем пользователя с таким же логином в базе данных
        user = User.query.filter_by(login=self.login.data).first()
        # Если пользователь найден, вызываем ошибку валидации
        if user:
            raise ValidationError('Данное имя пользователя уже занято', 'danger')


# Класс формы для авторизации пользователей
class LoginForm(FlaskForm):
    # Поле для ввода логина
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    
    # Поле для ввода пароля
    password = PasswordField('Пароль', validators=[DataRequired()])
    
    # Кнопка отправки формы
    submit = SubmitField('Войти')