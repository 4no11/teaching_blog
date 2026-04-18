from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Post, Category, User, Comment
from werkzeug.security import check_password_hash
from sqlalchemy import or_
import re

client_bp = Blueprint('client', __name__)

def make_slug(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug

@client_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category')
    post_type = request.args.get('type')
    
    query = Post.query.filter_by(is_published=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if post_type:
        query = query.filter_by(post_type=post_type)
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    categories = Category.query.all()
    return render_template('client/index.html', posts=posts, categories=categories)

@client_bp.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    post.views += 1
    db.session.commit()
    
    categories = Category.query.all()
    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).order_by(Comment.created_at.desc()).all()
    
    return render_template('client/post.html', post=post, categories=categories, comments=comments)

@client_bp.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(category_id=category.id, is_published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    categories = Category.query.all()
    return render_template('client/category.html', category=category, posts=posts, categories=categories)

@client_bp.route('/type/<post_type>')
def post_type(post_type):
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(post_type=post_type, is_published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    categories = Category.query.all()
    type_names = {'note': '教学笔记', 'resource': '教育资源', 'experience': '教育心得'}
    return render_template('client/type.html', posts=posts, categories=categories, 
                           post_type=post_type, type_name=type_names.get(post_type, post_type))

@client_bp.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    
    if keyword:
        posts = Post.query.filter(
            or_(Post.title.contains(keyword), Post.content.contains(keyword)),
            Post.is_published==True
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    else:
        posts = []
    
    categories = Category.query.all()
    return render_template('client/search.html', posts=posts, keyword=keyword, categories=categories)

@client_bp.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    content = request.form.get('content')
    parent_id = request.form.get('parent_id', type=int)
    
    if content and session.get('user_id'):
        comment = Comment(
            content=content,
            post_id=post_id,
            user_id=session['user_id'],
            parent_id=parent_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('评论成功！', 'success')
    else:
        flash('请先登录后再评论', 'warning')
    
    post = Post.query.get_or_404(post_id)
    return redirect(url_for('client.post_detail', slug=post.slug))

@client_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('client.index'))
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('client/login.html')

@client_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('已退出登录', 'info')
    return redirect(url_for('client.index'))

@client_bp.route('/about')
def about():
    categories = Category.query.all()
    return render_template('client/about.html', categories=categories)
