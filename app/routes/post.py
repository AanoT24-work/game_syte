from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
import os

from app.functions import save_picture
from ..extensions import db
from ..form import PostForm, CommentForm
from ..models.post import Post, Comment

post = Blueprint('post', __name__)

@post.route('/posts')
def all_posts():
    """Главная страница со всеми постами"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.options(db.joinedload(Post.user))\
                      .order_by(Post.created_at.desc())\
                      .paginate(page=page, per_page=10)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        posts_data = []
        for post_item in posts.items:
            post_data = {
                'id': post_item.id,
                'content': post_item.content,
                'image': post_item.image,
                'created_at': post_item.created_at.strftime('%d.%m.%Y %H:%M'),
                'user': {
                    'id': post_item.user.id,
                    'login': post_item.user.login,
                    'avatar': post_item.user.avatar
                },
                'likes_count': post_item.likes_count,
                'user_has_liked': post_item.user_has_liked(current_user.id) if current_user.is_authenticated else False
            }
            posts_data.append(post_data)
        
        return jsonify({
            'posts': posts_data,
            'has_next': posts.has_next
        })
    
    return render_template('post/all.html', posts=posts)

@post.route('/post/create', methods=['POST', 'GET'])
@login_required
def create_post():
    """Создание нового поста"""
    form = PostForm()
    
    if form.validate_on_submit():
        try:
            image_filename = None
            if form.image.data:
                image_filename = save_picture(form.image.data, image_type='post')
            
            post = Post(
                content=form.content.data,
                image=image_filename,
                user_id=current_user.id
            )
            
            db.session.add(post)
            db.session.commit()
            
            flash('Пост успешно создан!', 'success')
            return redirect(url_for('post.all_posts'))
        
        except Exception as e:
            db.session.rollback()
            flash('При создании поста возникла ошибка', 'danger')
    
    return render_template('post/create.html', form=form)

@post.route('/post/<int:post_id>')
def post_detail(post_id):
    """Детальная страница поста"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    return render_template('post/detail.html', post=post, form=form)

@post.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Удаление поста"""
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        flash('Вы не можете удалить этот пост', 'danger')
        return redirect(url_for('post.post_detail', post_id=post_id))
    
    try:
        if post.image:
            image_path = os.path.join(
                current_app.root_path, 
                'static', 'upload', 'posts', 
                post.image
            )
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(post)
        db.session.commit()
        flash('Пост успешно удален!', "success")
        
    except Exception as e:
        db.session.rollback()
        flash('При удалении поста возникла ошибка', 'danger')
    
    return redirect(url_for('user.accaunt'))

@post.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Лайк/анлайк поста"""
    try:
        post = Post.query.get_or_404(post_id)
        
        # Инициализируем если None
        if post.liked_by is None:
            post.liked_by = []
        
        # СОЗДАЕМ КОПИЮ списка для работы
        current_likes = list(post.liked_by)
        user_id = current_user.id
        
        if user_id in current_likes:
            # Убираем лайк из копии
            current_likes.remove(user_id)
            liked = False
        else:
            # Добавляем лайк в копию
            current_likes.append(user_id)
            liked = True
        
        # ПРИСВАИВАЕМ новый список обратно
        post.liked_by = current_likes
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'liked': liked,
            'likes_count': len(post.liked_by)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@post.route('/post/image/<int:post_id>')
def get_post_image(post_id):
    """Просмотр изображения поста"""
    post = Post.query.get_or_404(post_id)
    
    if post.image:
        return send_from_directory(
            os.path.join(current_app.root_path, 'static', 'upload', 'posts'),
            post.image
        )
    
    return "Изображение не найдено", 404

@post.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Добавление комментария к посту"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        try:
            comment = Comment(
                text=form.text.data,
                user_id=current_user.id,
                post_id=post_id
            )
            
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий добавлен!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении комментария', 'danger')
    
    return redirect(url_for('post.post_detail', post_id=post_id))

@post.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Удаление комментария"""
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id:
        flash('Вы не можете удалить этот комментарий', 'danger')
        return redirect(url_for('post.post_detail', post_id=comment.post_id))
    
    try:
        db.session.delete(comment)
        db.session.commit()
        flash('Комментарий удален!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении комментария', 'danger')
    
    return redirect(url_for('post.post_detail', post_id=comment.post_id))

@post.route('/post/create-ajax', methods=['POST'])
@login_required
def create_ajax():
    """Создание поста через AJAX"""
    try:
        content = request.form.get('content')
        image = request.files.get('image')
        
        if not content:
            return jsonify({'success': False, 'error': 'Текст поста обязателен'})
        
        # Сохраняем изображение если есть
        image_filename = None
        if image and image.filename:
            image_filename = save_picture(image, image_type='post')
        
        # Создаем пост
        post = Post(
            content=content,
            image=image_filename,
            user_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Пост успешно создан!',
            'post_id': post.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
