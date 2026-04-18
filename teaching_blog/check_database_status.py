#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Post, User, Category, Comment, Favorite, ReadingHistory

def check_database_status():
    """全面检查数据库状态"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("📊 数据库状态全面检查")
        print("=" * 80)
        
        try:
            print(f"🔍 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🗄️  数据库连接: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else '配置异常'}")
            print()
            
            # 1. 检查所有表的数据量
            print("📈 数据统计:")
            print("-" * 40)
            
            tables_stats = {
                '用户表 (User)': User.query.count(),
                '文章表 (Post)': Post.query.count(),
                '分类表 (Category)': Category.query.count(),
                '评论表 (Comment)': Comment.query.count(),
                '收藏表 (Favorite)': Favorite.query.count(),
                '阅读历史表 (ReadingHistory)': ReadingHistory.query.count()
            }
            
            for table_name, count in tables_stats.items():
                print(f"  {table_name}: {count} 条记录")
            
            print()
            
            # 2. 检查文章的详细状态
            print("📝 文章详细状态:")
            print("-" * 40)
            
            total_posts = Post.query.count()
            published_posts = Post.query.filter_by(is_published=True).count()
            draft_posts = Post.query.filter_by(is_published=False).count()
            
            print(f"  总文章数: {total_posts}")
            print(f"  已发布: {published_posts}")
            print(f"  草稿: {draft_posts}")
            print()
            
            # 3. 显示所有文章（按时间排序）
            print("📋 所有文章列表 (按创建时间降序):")
            print("-" * 40)
            print(f"{'ID':<4} {'标题':<30} {'状态':<8} {'类型':<10} {'创建时间':<20}")
            print("-" * 80)
            
            all_posts = Post.query.order_by(Post.created_at.desc()).all()
            for post in all_posts:
                status = "✅已发布" if post.is_published else "📝草稿"
                title_short = post.title[:28] + ".." if len(post.title) > 30 else post.title
                print(f"{post.id:<4} {title_short:<30} {status:<8} {post.post_type:<10} {post.created_at}")
            
            print()
            
            # 4. 检查最近的评论
            print("💬 评论统计:")
            print("-" * 40)
            
            total_comments = Comment.query.count()
            recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
            
            print(f"  总评论数: {total_comments}")
            print("  最近5条评论:")
            
            if recent_comments:
                for comment in recent_comments:
                    post = Post.query.get(comment.post_id)
                    post_title = post.title if post else "未知文章"
                    print(f"    - ID={comment.id}, 文章='{post_title}', 评论='{comment.content[:30]}...'")
            else:
                print("    暂无评论")
            
            print()
            
            # 5. 检查用户信息
            print("👥 用户信息:")
            print("-" * 40)
            
            users = User.query.all()
            for user in users:
                post_count = Post.query.filter_by(author_id=user.id).count()
                print(f"  用户: {user.username} (ID={user.id}), 发布文章: {post_count} 篇")
            
            print()
            
            # 6. 检查分类信息
            print("📂 分类信息:")
            print("-" * 40)
            
            categories = Category.query.all()
            for category in categories:
                post_count = Post.query.filter_by(category_id=category.id).count()
                print(f"  分类: {category.name} (ID={category.id}), 文章数: {post_count}")
            
            print()
            
            # 7. 检查数据库连接是否正常
            print("🔗 数据库连接测试:")
            print("-" * 40)
            
            try:
                # 测试写入
                test_post = Post(
                    title="数据库连接测试",
                    slug="test-connection",
                    content="测试内容",
                    summary="测试摘要",
                    post_type="test",
                    category_id=1,
                    author_id=1,
                    is_published=False
                )
                db.session.add(test_post)
                db.session.flush()  # 获取ID但不提交
                
                # 测试读取
                read_test = Post.query.get(test_post.id)
                if read_test:
                    print("  ✅ 数据库连接正常 (读写测试通过)")
                else:
                    print("  ❌ 数据库读取测试失败")
                
                # 回滚测试数据
                db.session.rollback()
                
            except Exception as e:
                print(f"  ❌ 数据库连接异常: {str(e)}")
            
            print()
            print("=" * 80)
            print("✅ 数据库状态检查完成")
            print("=" * 80)
            
            # 8. 如果确实有数据，提示用户如何查看
            if total_posts > 0:
                print()
                print("💡 如果您在数据库管理工具中看不到数据，请检查:")
                print("  1. 是否连接到正确的数据库")
                print("  2. 数据库管理工具是否需要刷新")
                print("  3. 是否查看的是正确的表名")
                print("  4. 当前应用是否使用不同的数据库配置文件")
            
        except Exception as e:
            print(f"❌ 检查过程出错: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_database_status()