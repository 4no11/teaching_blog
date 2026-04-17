from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    cover_image = db.Column(db.String(300))
    post_type = db.Column(db.String(20), default='note')  # note, resource, experience
    is_published = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.title}>'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(300))
    bio = db.Column(db.String(500))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    user = db.relationship('User', backref='comments')
    post = db.relationship('Post', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def __repr__(self):
        return f'<Comment {self.id}>'

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    file_path = db.Column(db.String(300), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return f'<Resource {self.name}>'

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='favorites')
    post = db.relationship('Post', backref='favorited_by')

    def __repr__(self):
        return f'<Favorite user={self.user_id} post={self.post_id}>'

class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', foreign_keys=[user_id], backref='following')
    author = db.relationship('User', foreign_keys=[author_id], backref='followers')

    def __repr__(self):
        return f'<Follow user={self.user_id} author={self.author_id}>'

class ReadingHistory(db.Model):
    __tablename__ = 'reading_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_duration = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='reading_history')
    post = db.relationship('Post', backref='read_by')

    def __repr__(self):
        return f'<ReadingHistory user={self.user_id} post={self.post_id}>'

class InternationalEducation(db.Model):
    __tablename__ = 'international_education'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    organization = db.Column(db.String(200))
    country = db.Column(db.String(100))
    source_url = db.Column(db.String(1000))
    source_name = db.Column(db.String(100))
    content = db.Column(db.Text)
    topic = db.Column(db.String(100))
    publish_date = db.Column(db.DateTime)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<InternationalEducation {self.title[:30]}...>'

class EducationNewsSource(db.Model):
    __tablename__ = 'education_news_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    source_type = db.Column(db.String(50))
    country = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_fetched = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EducationNewsSource {self.name}>'

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(1000), nullable=False)
    thumbnail_url = db.Column(db.String(1000))
    source_name = db.Column(db.String(100))
    source_url = db.Column(db.String(1000))
    duration = db.Column(db.Integer)  # in seconds
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    publish_date = db.Column(db.DateTime)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Video {self.title[:30]}...>'

class ContentNode(db.Model):
    """学习内容节点模型"""
    __tablename__ = 'content_nodes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('content_nodes.id'))
    level = db.Column(db.Integer, default=1)  # 节点层级
    order_index = db.Column(db.Integer, default=0)  # 排序索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    parent = db.relationship('ContentNode', remote_side=[id], backref='children')
    progress_records = db.relationship('LearningProgress', backref='content_node')

class LearningProgress(db.Model):
    """学习进度模型"""
    __tablename__ = 'learning_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_node_id = db.Column(db.Integer, db.ForeignKey('content_nodes.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    comprehension_level = db.Column(db.Integer, default=0)  # 0-100，理解程度
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent = db.Column(db.Integer, default=0)  # 单位：秒
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='learning_progress')

class ComprehensionRecord(db.Model):
    """理解程度记录模型"""
    __tablename__ = 'comprehension_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_node_id = db.Column(db.Integer, db.ForeignKey('content_nodes.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)  # 测试问题
    answer = db.Column(db.Text, nullable=False)  # 学生回答
    score = db.Column(db.Integer, default=0)  # 得分
    feedback = db.Column(db.Text)  # 反馈
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='comprehension_records')
    content_node = db.relationship('ContentNode', backref='comprehension_records')


