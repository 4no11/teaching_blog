#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Post, Comment

def quick_check():
    """快速数据验证"""
    app = create_app()
    
    with app.app_context():
        print("🔍 快速数据验证")
        print("-" * 40)
        
        # 检查文章
        posts = Post.query.all()
        print(f"📝 文章总数: {len(posts)}")
        
        if posts:
            print("📋 最近的文章:")
            for post in posts[-3:]:  # 显示最近3篇
                print(f"  - ID{post.id}: {post.title[:30]}{'...' if len(post.title) > 30 else ''}")
        
        # 检查评论
        comments = Comment.query.all()
        print(f"💬 评论总数: {len(comments)}")
        
        if comments:
            print("💬 最近的评论:")
            for comment in comments[-2:]:  # 显示最近2条
                print(f"  - ID{comment.id}: {comment.content[:30]}{'...' if len(comment.content) > 30 else ''}")
        
        print("-" * 40)
        print("✅ 数据验证完成")

if __name__ == "__main__":
    quick_check()