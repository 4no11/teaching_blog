#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Post, Category

def test_publish_article():
    """测试文章发布功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始测试文章发布功能")
        print("=" * 60)
        
        try:
            # 检查数据库连接
            print(f"[DEBUG] 检查数据库连接...")
            user_count = User.query.count()
            post_count = Post.query.count()
            category_count = Category.query.count()
            
            print(f"[DEBUG] 数据库状态: 用户={user_count}, 文章={post_count}, 分类={category_count}")
            
            if category_count == 0:
                print("[ERROR] 没有可用分类，请先创建分类")
                return
            
            # 获取第一个用户和分类
            user = User.query.first()
            category = Category.query.first()
            
            if not user:
                print("[ERROR] 没有可用用户，请先创建用户")
                return
            
            print(f"[DEBUG] 使用用户: {user.username}, 分类: {category.name}")
            
            # 创建测试文章
            title = f"测试文章 {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            content = "这是一个测试文章的内容。\n\n## 测试标题\n\n这里是正文内容。"
            summary = "这是一个测试文章的摘要"
            post_type = "blog"
            
            print(f"[DEBUG] 创建测试文章...")
            print(f"[DEBUG] 标题: {title}")
            print(f"[DEBUG] 类型: {post_type}")
            print(f"[DEBUG] 分类ID: {category.id}")
            
            # 创建文章对象
            from routes.client import make_slug
            slug = make_slug(title)
            print(f"[DEBUG] 生成slug: {slug}")
            
            new_post = Post(
                title=title,
                slug=slug,
                content=content,
                summary=summary,
                post_type=post_type,
                category_id=category.id,
                author_id=user.id,
                is_published=True,  # 直接设置为已发布
                cover_image=None,
                views=0
            )
            
            print(f"[DEBUG] 添加文章到数据库会话...")
            db.session.add(new_post)
            
            print(f"[DEBUG] 提交数据库事务...")
            db.session.commit()
            
            print(f"[DEBUG] 文章已保存到数据库, ID={new_post.id}, is_published={new_post.is_published}")
            
            # 验证文章是否真的被保存到数据库
            print(f"[DEBUG] 开始验证数据库提交...")
            committed_post = Post.query.get(new_post.id)
            if committed_post:
                print(f"[DEBUG] 验证成功: 找到文章 ID={committed_post.id}, title={committed_post.title}")
                print(f"[DEBUG] 文章状态: is_published={committed_post.is_published}, slug={committed_post.slug}")
                
                # 检查首页会显示的文章数量
                published_posts = Post.query.filter_by(is_published=True).count()
                draft_posts = Post.query.filter_by(is_published=False).count()
                print(f"[DEBUG] 数据库统计: 已发布={published_posts}, 草稿={draft_posts}")
                
                print("=" * 60)
                print("✅ 测试成功！文章发布功能正常")
                print("=" * 60)
                return True
            else:
                print(f"[DEBUG] 验证失败: 未找到文章 ID={new_post.id}")
                print("=" * 60)
                print("❌ 测试失败！文章未被正确保存")
                print("=" * 60)
                return False
                
        except Exception as e:
            print(f"[DEBUG] 测试过程出错: {str(e)}")
            print(f"[DEBUG] 异常类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print("=" * 60)
            print("❌ 测试失败！出现异常")
            print("=" * 60)
            return False

if __name__ == "__main__":
    test_publish_article()