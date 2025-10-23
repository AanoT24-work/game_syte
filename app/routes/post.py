from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from ..models.post import Post

post = Blueprint('post', __name__)

@post.route('/', methods = ['POST', 'GET'])
@login_required  # Добавляем декоратор для проверки авторизации
def all():
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('post/all.html', posts=posts)