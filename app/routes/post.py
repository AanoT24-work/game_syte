from flask import Blueprint, render_template

from ..models.user import User

from ..models.post import Post

from ..extensions import db

post = Blueprint('post', __name__)

@post.route('/', methods = ['POST', 'GET'])
def all():
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('post/all.html', posts=posts, user=User)