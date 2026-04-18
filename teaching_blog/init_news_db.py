import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, EducationNewsSource
from services.news_service import init_news_sources, crawl_and_update_news

def init_database():
    app = create_app()
    with app.app_context():
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建完成！")

        print("正在初始化新闻源...")
        init_news_sources()
        print("新闻源初始化完成！")

        print("正在获取国际教育资讯...")
        try:
            count = crawl_and_update_news()
            print(f"成功获取 {count} 条国际教育资讯！")
        except Exception as e:
            print(f"获取资讯时出错: {e}")
            print("这可能是因为网络连接问题，请在应用启动后通过网页手动刷新。")

        print("\n初始化完成！请启动应用访问 /international-news 查看国际教育动态。")

if __name__ == '__main__':
    init_database()
