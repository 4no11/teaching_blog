import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:{os.environ.get('DB_PASSWORD', '123456')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', 3306)}/{os.environ.get('DB_NAME', 'teaching_blog')}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI大模型配置 - 硅基流动 (免费500万token)
    # 注册地址: https://siliconflow.cn
    # 配置方式：set AI_API_KEY=你的API密钥
    AI_API_KEY = os.environ.get('AI_API_KEY') or 'sk-meqhrwnstykacbxnjcwwpsxcwfzkvzzldnwbookzphpjhvlx'
    AI_BASE_URL = os.environ.get('AI_BASE_URL') or 'https://api.siliconflow.cn/v1'
    AI_MODEL = os.environ.get('AI_MODEL') or 'deepseek-ai/DeepSeek-V2.5'
    
    # 分页配置
    POSTS_PER_PAGE = 10
    ADMIN_POSTS_PER_PAGE = 20
