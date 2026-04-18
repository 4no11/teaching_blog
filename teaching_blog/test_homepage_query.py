#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Post, Category, User

def test_homepage_query():
    """测试首页查询逻辑"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("测试首页查询逻辑")
        print("=" * 60)
        
        try:
            # 模拟首页的查询逻辑
            print("[DEBUG] 模拟首页查询...")
            
            # 第一页查询
            page = 1
            category_id = None
            post_type = None
            
            query = Post.query.filter_by(is_published=True)
            
            if category_id:
                query = query.filter_by(category_id=category_id)
            if post_type:
                query = query.filter_by(post_type=post_type)
            
            posts = query.order_by(Post.created_at.desc()).paginate(
                page=page, per_page=10, error_out=False
            )
            
            print(f"[DEBUG] 首页查询结果:")
            print(f"[DEBUG] 当前页: {page}")
            print(f"[DEBUG] 总页数: {posts.pages}")
            print(f"[DEBUG] 当前页文章数: {len(posts.items)}")
            print(f"[DEBUG] 总文章数: {posts.total}")
            
            print("\n[DEBUG] 首页显示的文章:")
            for i, post in enumerate(posts.items, 1):
                print(f"{i}. ID={post.id}, 标题='{post.title}', 创建时间={post.created_at}, 类型={post.post_type}")
            
            # 检查刚发布的测试文章是否在首页
            test_post = Post.query.filter_by(title="测试文章 20251230_150541").first()
            if test_post:
                print(f"\n✅ 找到测试文章: ID={test_post.id}, 在第{posts.pages}页")
                
                # 检查文章是否在前10篇中
                if test_post in posts.items:
                    print("✅ 测试文章在首页第一页显示")
                else:
                    print("❌ 测试文章不在首页第一页")
                    
                    # 计算文章在第几页
                    all_posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
                    post_index = next((i for i, p in enumerate(all_posts) if p.id == test_post.id), -1)
                    if post_index >= 0:
                        page_number = (post_index // 10) + 1
                        print(f"[DEBUG] 测试文章在第{page_number}页 (索引={post_index})")
            else:
                print("\n❌ 未找到测试文章")
            
            # 显示所有已发布的文章（按时间排序）
            print(f"\n[DEBUG] 所有已发布文章 (按创建时间降序):")
            all_published = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
            for i, post in enumerate(all_published, 1):
                print(f"{i}. ID={post.id}, 标题='{post.title}', 创建时间={post.created_at}")
            
            print("=" * 60)
            print("✅ 首页查询测试完成")
            print("=" * 60)
            
        except Exception as e:
            print(f"[DEBUG] 测试过程出错: {str(e)}")
            print(f"[DEBUG] 异常类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_homepage_query()