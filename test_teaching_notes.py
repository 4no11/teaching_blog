#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试脚本：检查教学笔记分类中的文章"""

import sys
import os

# 添加项目目录到 Python 路径
project_dir = os.path.join(os.path.dirname(__file__), 'teaching_blog')
sys.path.insert(0, project_dir)
os.chdir(project_dir)

from app import create_app
from models import Post, Category

def check_teaching_notes():
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("[教学笔记分类文章检查报告]")
        print("=" * 60)
        
        # 1. 检查所有已发布的文章
        print("\n[所有已发布文章列表]:")
        print("-" * 40)
        all_posts = Post.query.filter_by(is_published=True).all()
        
        if not all_posts:
            print("[!] 没有找到任何已发布的文章！")
        else:
            for post in all_posts:
                print(f"  [OK] ID:{post.id} | {post.title[:30]}... | 类型:{post.post_type} | 状态:已发布")
                print(f"      Slug: {post.slug}")
                print(f"      分类: {post.category.name if post.category else '无'}")
                print()
        
        # 2. 专门检查教学笔记 (post_type='note')
        print("\n[教学笔记 (post_type='note') 文章]:")
        print("-" * 40)
        note_posts = Post.query.filter_by(post_type='note', is_published=True).all()
        
        if not note_posts:
            print("[!] 没有找到教学笔记类型的文章！")
        else:
            print(f"共找到 {len(note_posts)} 篇教学笔记：\n")
            for i, post in enumerate(note_posts, 1):
                print(f"{i}. {post.title}")
                print(f"   - Slug: {post.slug}")
                print(f"   - 创建时间: {post.created_at.strftime('%Y-%m-%d %H:%M')}")
                print(f"   - 浏览量: {post.views}")
                print(f"   - 评论数: {len(post.comments)}")
                print()
        
        # 3. 检查分类表
        print("\n[文章分类列表]:")
        print("-" * 40)
        categories = Category.query.all()
        for cat in categories:
            count = Post.query.filter_by(category_id=cat.id, is_published=True).count()
            print(f"  [{cat.name}] (slug: {cat.slug}) - {count} 篇文章")
        
        # 4. 总结
        print("\n" + "=" * 60)
        print("[统计摘要]")
        print("=" * 60)
        print(f"总文章数: {len(all_posts)}")
        print(f"教学笔记数: {len(note_posts)}")
        print(f"教育资源数: {Post.query.filter_by(post_type='resource', is_published=True).count()}")
        print(f"教育心得数: {Post.query.filter_by(post_type='experience', is_published=True).count()}")
        
        if note_posts:
            print("\n[成功] 教学笔记页面应该能正常显示文章。")
            print(f"\n访问地址: http://127.0.0.1:5000/type/teaching-notes")
            print(f"\n最新文章详情: http://127.0.0.1:5000/post/{note_posts[0].slug}")
        else:
            print("\n[警告] 没有教学笔记类型的文章！")
            print("请先发布一篇教学笔记类型的文章后再测试。")

if __name__ == '__main__':
    try:
        check_teaching_notes()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
