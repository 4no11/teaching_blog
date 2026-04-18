from app import create_app
from services.video_service import crawl_and_update_videos, add_sample_videos

# 初始化应用
app = create_app()

with app.app_context():
    print("=== 初始化视频数据 ===")
    print("正在添加示例视频...")
    count = add_sample_videos()
    print(f"成功添加 {count} 个示例视频")
    print("=== 初始化完成 ===")
