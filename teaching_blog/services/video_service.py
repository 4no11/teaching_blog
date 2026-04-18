from datetime import datetime, timedelta
from models import db, Video
from services.video_crawler import VideoCrawler, FeaturedVideoSelector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sample_videos():
    """添加示例视频，确保视频中心有内容"""
    sample_videos = [
        {
            'title': '如何使用Python进行数据分析',
            'description': '本视频介绍了Python在数据分析中的应用，包括NumPy、Pandas等库的使用方法。',
            'video_url': 'https://www.bilibili.com/video/BV1Ex411x7nb',
            'thumbnail_url': 'https://picsum.photos/id/1001/600/338',
            'source_name': 'Bilibili',
            'source_url': 'https://www.bilibili.com/',
            'category': 'Programming',
            'publish_date': datetime.utcnow() - timedelta(days=5)
        },
        {
            'title': '机器学习基础教程',
            'description': '从零基础开始学习机器学习，包括监督学习、无监督学习等核心概念。',
            'video_url': 'https://www.bilibili.com/video/BV1Mh411e7VU',
            'thumbnail_url': 'https://picsum.photos/id/1002/600/338',
            'source_name': 'Bilibili',
            'source_url': 'https://www.bilibili.com/',
            'category': 'Machine Learning',
            'publish_date': datetime.utcnow() - timedelta(days=10)
        },
        {
            'title': '深度学习与神经网络',
            'description': '深入讲解深度学习和神经网络的原理，包括CNN、RNN等经典模型。',
            'video_url': 'https://www.bilibili.com/video/BV1Jx411L7LU',
            'thumbnail_url': 'https://picsum.photos/id/1003/600/338',
            'source_name': 'Bilibili',
            'source_url': 'https://www.bilibili.com/',
            'category': 'Deep Learning',
            'publish_date': datetime.utcnow() - timedelta(days=15)
        },
        {
            'title': '教育心理学在教学中的应用',
            'description': '探讨教育心理学原理如何提升教学效果，帮助教师更好地理解学生。',
            'video_url': 'https://www.bilibili.com/video/BV1xx411c7mZ',
            'thumbnail_url': 'https://picsum.photos/id/1005/600/338',
            'source_name': 'Bilibili',
            'source_url': 'https://www.bilibili.com/',
            'category': 'Education',
            'publish_date': datetime.utcnow() - timedelta(days=20)
        },
        {
            'title': '在线课程设计最佳实践',
            'description': '分享在线课程设计的最佳实践和实用技巧，提高课程质量。',
            'video_url': 'https://www.bilibili.com/video/BV1kx411c7mZ',
            'thumbnail_url': 'https://picsum.photos/id/1006/600/338',
            'source_name': 'Bilibili',
            'source_url': 'https://www.bilibili.com/',
            'category': 'Education Technology',
            'publish_date': datetime.utcnow() - timedelta(days=25)
        }
    ]
    
    existing_urls = set()
    existing = Video.query.all()
    for item in existing:
        if item.video_url:
            existing_urls.add(item.video_url)
    
    new_count = 0
    for video in sample_videos:
        if video['video_url'] in existing_urls:
            continue
    
        try:
            video_item = Video(
                title=video['title'][:500],
                description=video.get('description', ''),
                video_url=video['video_url'],
                thumbnail_url=video.get('thumbnail_url', ''),
                source_name=video['source_name'],
                source_url=video['source_url'],
                category=video.get('category', 'Education'),
                publish_date=video.get('publish_date', datetime.utcnow()),
                is_featured=True
            )
            db.session.add(video_item)
            existing_urls.add(video['video_url'])
            new_count += 1
        except Exception as e:
            logger.error(f"Error saving sample video: {e}")
            continue
    
    if new_count > 0:
        db.session.commit()
        logger.info(f"Added {new_count} sample videos")
    
    return new_count

def crawl_and_update_videos():
    logger.info("Starting video crawl...")
    crawler = VideoCrawler()
    selector = FeaturedVideoSelector()

    videos = crawler.crawl_all_sources()
    logger.info(f"Total videos fetched: {len(videos)}")

    # 如果没有爬取到视频，添加示例视频
    if not videos:
        logger.info("No videos fetched, adding sample videos...")
        return add_sample_videos()

    featured_videos = selector.select_featured(videos, limit=30)
    logger.info(f"Featured videos: {len(featured_videos)}")

    existing_urls = set()
    existing = Video.query.all()
    for item in existing:
        if item.video_url:
            existing_urls.add(item.video_url)

    new_count = 0
    for video in featured_videos:
        if video['video_url'] in existing_urls:
            continue

        try:
            video_item = Video(
                title=video['title'][:500],
                description=video.get('description', ''),
                video_url=video['video_url'],
                thumbnail_url=video.get('thumbnail_url', ''),
                source_name=video['source_name'],
                source_url=video['source_url'],
                category=video.get('category', 'Education'),
                publish_date=video.get('publish_date', datetime.utcnow()),
                is_featured=True
            )
            db.session.add(video_item)
            existing_urls.add(video['video_url'])
            new_count += 1
        except Exception as e:
            logger.error(f"Error saving video: {e}")
            continue

    # 如果爬取到的视频数量较少，添加示例视频
    if new_count < 5:
        logger.info("Adding sample videos to supplement...")
        new_count += add_sample_videos()

    db.session.commit()

    old_date = datetime.utcnow() - timedelta(days=30)
    deleted = Video.query.filter(Video.fetched_at < old_date).delete()
    if deleted > 0:
        db.session.commit()
        logger.info(f"Cleaned up {deleted} old videos")

    logger.info(f"Added {new_count} new videos")
    return new_count

def get_latest_videos(page=1, per_page=12, category=None):
    query = Video.query.filter_by(is_featured=True)

    if category:
        query = query.filter(Video.category == category)

    return query.order_by(Video.publish_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

def get_featured_videos(limit=6):
    return Video.query\
        .filter_by(is_featured=True)\
        .order_by(Video.publish_date.desc())\
        .limit(limit)\
        .all()

def get_video_categories():
    categories = db.session.query(
        Video.category,
        db.func.count(Video.id)
    ).filter(Video.is_featured == True)\
     .group_by(Video.category)\
     .all()

    return [{'name': c[0], 'count': c[1]} for c in categories if c[0]]

