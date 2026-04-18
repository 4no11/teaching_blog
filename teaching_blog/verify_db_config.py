#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Post

def verify_database_config():
    """验证当前应用使用的数据库配置"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔍 数据库配置验证")
        print("=" * 60)
        
        # 显示数据库连接字符串
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"🗄️  当前数据库连接: {db_uri}")
        
        # 解析数据库信息
        if 'mysql' in db_uri:
            print("📊 数据库类型: MySQL")
            
            # 解析连接参数
            parts = db_uri.replace('mysql+pymysql://', '').split('@')
            if len(parts) == 2:
                user_pass = parts[0].split(':')
                host_db = parts[1].split('/')
                
                if len(user_pass) >= 2 and len(host_db) >= 2:
                    username = user_pass[0]
                    password = '*' * len(user_pass[1]) if user_pass[1] else '(空密码)'
                    host_info = host_db[0]
                    database = host_db[1].split('?')[0]
                    
                    print(f"👤 用户名: {username}")
                    print(f"🔒 密码: {password}")
                    print(f"🌐 主机: {host_info}")
                    print(f"📂 数据库: {database}")
        
        print()
        
        # 测试数据库连接
        try:
            print("🔗 测试数据库连接...")
            result = db.session.execute(db.text("SELECT 1")).fetchone()
            if result:
                print("✅ 数据库连接成功")
            else:
                print("❌ 数据库连接失败")
        except Exception as e:
            print(f"❌ 数据库连接异常: {str(e)}")
        
        print()
        
        # 显示当前数据量确认
        try:
            post_count = Post.query.count()
            print(f"📝 当前文章数量: {post_count}")
            
            if post_count > 0:
                latest_post = Post.query.order_by(Post.created_at.desc()).first()
                print(f"🕒 最新文章: {latest_post.title} (创建时间: {latest_post.created_at})")
                
                print("\n💡 如果您在外部数据库工具中看不到数据：")
                print("   1. 请确保连接的是同一个数据库")
                print("   2. 使用上述连接参数")
                print("   3. 查看 'posts' 表（不是 'post'）")
                print("   4. 刷新数据库工具缓存")
        
        except Exception as e:
            print(f"❌ 查询数据时出错: {str(e)}")
        
        print()
        print("=" * 60)

if __name__ == "__main__":
    verify_database_config()