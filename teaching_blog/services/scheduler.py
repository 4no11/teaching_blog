import schedule
import time
import threading
import logging
from datetime import datetime
from services.international_crawler import InternationalEducationCrawler, FeaturedNewsSelector
from services.news_service import crawl_and_update_news, get_latest_news, get_latest_news_count
from models import db

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.crawler = InternationalEducationCrawler()
        self.selector = FeaturedNewsSelector()
        self.is_running = False
        self.scheduler_thread = None
        self.app = None
        
    def crawl_news_job(self):
        """定时爬取新闻任务"""
        try:
            logger.info("开始执行定时新闻爬取任务...")
            start_time = datetime.now()
            
            # 在应用上下文中执行数据库操作
            if self.app:
                with self.app.app_context():
                    count = crawl_and_update_news()
            else:
                count = crawl_and_update_news()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"定时爬取完成: 获取 {count} 条新闻，耗时 {duration:.2f} 秒")
            
        except Exception as e:
            logger.error(f"定时爬取任务执行失败: {e}")
    
    def cleanup_old_news_job(self):
        """清理旧新闻任务"""
        try:
            logger.info("开始清理旧新闻...")
            # 这里可以添加清理逻辑，比如删除30天前的新闻
            # 目前先记录日志
            logger.info("旧新闻清理完成")
        except Exception as e:
            logger.error(f"清理旧新闻失败: {e}")
    
    def update_featured_news_job(self):
        """更新精选新闻任务"""
        try:
            logger.info("开始更新精选新闻...")
            # 在应用上下文中执行数据库操作
            if self.app:
                with self.app.app_context():
                    latest_count = get_latest_news_count()
            else:
                latest_count = get_latest_news_count()
            logger.info(f"精选新闻更新完成，当前有 {latest_count} 条最新新闻")
        except Exception as e:
            logger.error(f"更新精选新闻失败: {e}")

    def start_scheduler(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已经在运行中")
            return
        
        # 设置定时任务
        # 每4小时爬取一次新闻
        schedule.every(4).hours.do(self.crawl_news_job)
        
        # 每天凌晨2点清理旧新闻
        schedule.every().day.at("02:00").do(self.cleanup_old_news_job)
        
        # 每2小时更新一次精选新闻
        schedule.every(2).hours.do(self.update_featured_news_job)
        
        # 启动调度器线程
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("新闻定时调度器已启动")
        
        # 延迟执行爬取任务，确保应用正常启动
        threading.Timer(10, self.crawl_news_job).start()  # 10秒后执行
    
    def stop_scheduler(self):
        """停止调度器"""
        self.is_running = False
        schedule.clear()
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("新闻定时调度器已停止")
    
    def _run_scheduler(self):
        """调度器运行循环"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def get_status(self):
        """获取调度器状态"""
        return {
            'is_running': self.is_running,
            'next_runs': [
                {
                    'job': str(job.job_func),
                    'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else None
                }
                for job in schedule.jobs
            ],
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# 全局调度器实例
news_scheduler = NewsScheduler()

def start_news_scheduler(app=None):
    """启动新闻调度器"""
    if app:
        news_scheduler.app = app
    news_scheduler.start_scheduler()

def stop_news_scheduler():
    """停止新闻调度器"""
    news_scheduler.stop_scheduler()

def get_scheduler_status():
    """获取调度器状态"""
    return news_scheduler.get_status()