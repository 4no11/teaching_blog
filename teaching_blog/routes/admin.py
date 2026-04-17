from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Post, Category, User, Comment, Resource
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
import os
import re
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

def make_slug(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug

@admin_bp.route('/')
def dashboard():
    if not session.get('is_admin'):
        flash('请先登录管理员账号', 'warning')
        return redirect(url_for('admin.login'))
    
    stats = {
        'posts': Post.query.count(),
        'published': Post.query.filter_by(is_published=True).count(),
        'drafts': Post.query.filter_by(is_published=False).count(),
        'comments': Comment.query.count(),
        'users': User.query.count()
    }
    
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_posts=recent_posts)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # 特殊处理：如果是管理员账号且密码为 admin123，直接登录并重置密码
        if user and user.is_admin and username == 'admin' and password == 'admin123':
            # 重置密码为新的哈希类型
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
            from models import db
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('登录成功！密码已更新', 'success')
            return redirect(url_for('admin.dashboard'))
        elif user and user.is_admin and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('登录成功！', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('用户名或密码错误，或非管理员账号', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('client.index'))

@admin_bp.route('/posts')
def posts():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    query = Post.query
    if keyword:
        query = query.filter(or_(Post.title.contains(keyword), Post.content.contains(keyword)))
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/posts.html', posts=posts, keyword=keyword)

@admin_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        summary = request.form.get('summary')
        post_type = request.form.get('post_type')
        category_id = request.form.get('category_id', type=int)
        is_published = 'is_published' in request.form
        
        slug = make_slug(title)
        existing = Post.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{Post.query.count() + 1}"
        
        post = Post(
            title=title,
            slug=slug,
            content=content,
            summary=summary or content[:200],
            post_type=post_type,
            category_id=category_id,
            is_published=is_published,
            author_id=session['user_id']
        )
        
        db.session.add(post)
        db.session.commit()
        flash('文章创建成功！', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/post_form.html', categories=categories, post=None)

@admin_bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
def edit_post(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    post = Post.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.summary = request.form.get('summary')
        post.post_type = request.form.get('post_type')
        post.category_id = request.form.get('category_id', type=int)
        post.is_published = 'is_published' in request.form
        
        db.session.commit()
        flash('文章更新成功！', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/post_form.html', categories=categories, post=post)

@admin_bp.route('/post/<int:id>/delete')
def delete_post(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    post = Post.query.get_or_404(id)
    
    # 先删除相关的收藏记录
    from models import Favorite
    Favorite.query.filter_by(post_id=id).delete()
    
    # 删除相关的评论
    from models import Comment
    Comment.query.filter_by(post_id=id).delete()
    
    # 删除相关的资源
    from models import Resource
    Resource.query.filter_by(post_id=id).delete()
    
    # 删除相关的阅读历史
    from models import ReadingHistory
    ReadingHistory.query.filter_by(post_id=id).delete()
    
    # 最后删除文章
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect(url_for('admin.posts'))

@admin_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        slug = make_slug(name)
        description = request.form.get('description')
        
        if not Category.query.filter_by(slug=slug).first():
            category = Category(name=name, slug=slug, description=description)
            db.session.add(category)
            db.session.commit()
            flash('分类添加成功！', 'success')
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/category/<int:id>/delete')
def delete_category(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('分类已删除', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/comments')
def comments():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/comments.html', comments=comments)

@admin_bp.route('/comment/<int:id>/delete')
def delete_comment(id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('admin.comments'))

@admin_bp.route('/users')
def users():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        bio = request.form.get('bio')
        
        user = User.query.get(session['user_id'])
        user.username = username
        user.email = email
        user.bio = bio
        db.session.commit()
        session['username'] = username
        flash('个人信息已更新', 'success')
    
    user = User.query.get(session['user_id'])
    return render_template('admin/settings.html', user=user)

@admin_bp.route('/scheduler')
def scheduler():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    from services.scheduler import get_scheduler_status
    
    status = get_scheduler_status()
    return render_template('admin/scheduler.html', status=status)

@admin_bp.route('/scheduler/start', methods=['POST'])
def start_scheduler():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    try:
        from services.scheduler import start_news_scheduler
        start_news_scheduler()
        flash('定时调度器启动成功', 'success')
    except Exception as e:
        flash(f'启动失败: {str(e)}', 'danger')
    
    return redirect(url_for('admin.scheduler'))

@admin_bp.route('/scheduler/stop', methods=['POST'])
def stop_scheduler():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    try:
        from services.scheduler import stop_news_scheduler
        stop_news_scheduler()
        flash('定时调度器已停止', 'success')
    except Exception as e:
        flash(f'停止失败: {str(e)}', 'danger')
    
    return redirect(url_for('admin.scheduler'))

@admin_bp.route('/scheduler/trigger-crawl', methods=['POST'])
def trigger_crawl():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))
    
    try:
        from services.international_crawler import InternationalEducationCrawler, FeaturedNewsSelector
        from services.news_service import crawl_and_update_news
        
        count = crawl_and_update_news()
        flash(f'手动爬取完成，获取了 {count} 条新闻', 'success')
    except Exception as e:
        flash(f'爬取失败: {str(e)}', 'danger')
    
    return redirect(url_for('admin.scheduler'))
