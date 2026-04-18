from datetime import datetime, timedelta
from models import db, InternationalEducation, EducationNewsSource
from services.international_crawler import InternationalEducationCrawler, FeaturedNewsSelector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_news_sources():
    sources = [
        {'name': 'UNESCO', 'url': 'https://www.unesco.org/news', 'source_type': 'International Organization', 'country': 'International'},
        {'name': 'OECD Education', 'url': 'https://www.oecd.org/education/', 'source_type': 'International Organization', 'country': 'International'},
        {'name': 'World Bank Education', 'url': 'https://www.worldbank.org/en/topic/education', 'source_type': 'International Organization', 'country': 'International'},
        {'name': 'Education Week', 'url': 'https://www.edweek.org/', 'source_type': 'Media', 'country': 'United States'},
        {'name': 'Nature Education', 'url': 'https://www.nature.com/subjects/education', 'source_type': 'Academic Journal', 'country': 'United Kingdom'},
    ]

    for source_data in sources:
        existing = EducationNewsSource.query.filter_by(url=source_data['url']).first()
        if not existing:
            source = EducationNewsSource(**source_data)
            db.session.add(source)

    db.session.commit()
    logger.info("News sources initialized")

def crawl_and_update_news():
    logger.info("Starting news crawl...")
    crawler = InternationalEducationCrawler()
    selector = FeaturedNewsSelector()

    articles = crawler.crawl_all_sources()
    logger.info(f"Total articles fetched: {len(articles)}")

    if not articles:
        return 0

    featured_articles = selector.select_featured(articles, limit=15)
    logger.info(f"Featured articles: {len(featured_articles)}")

    existing_urls = set()
    existing = InternationalEducation.query.all()
    for item in existing:
        if item.source_url:
            existing_urls.add(item.source_url)

    new_count = 0
    for article in featured_articles:
        if article['source_url'] in existing_urls:
            continue

        try:
            news_item = InternationalEducation(
                title=article['title'][:500],
                organization=article.get('organization', ''),
                country=article.get('country', ''),
                source_url=article['source_url'],
                source_name=article['source_name'],
                content=article.get('content', ''),
                topic=article.get('topic', 'Education'),
                publish_date=article.get('publish_date', datetime.utcnow()),
                is_featured=True
            )
            db.session.add(news_item)
            existing_urls.add(article['source_url'])
            new_count += 1
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            continue

    db.session.commit()

    old_date = datetime.utcnow() - timedelta(days=90)
    deleted = InternationalEducation.query.filter(InternationalEducation.fetched_at < old_date).delete()
    if deleted > 0:
        db.session.commit()
        logger.info(f"Cleaned up {deleted} old articles")

    logger.info(f"Added {new_count} new articles")
    return new_count

def get_latest_news(page=1, per_page=10, topic=None):
    query = InternationalEducation.query.filter_by(is_featured=True)

    if topic:
        query = query.filter(InternationalEducation.topic == topic)

    return query.order_by(InternationalEducation.publish_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

def get_topics():
    topics = db.session.query(
        InternationalEducation.topic,
        db.func.count(InternationalEducation.id)
    ).filter(InternationalEducation.is_featured == True)\
     .group_by(InternationalEducation.topic)\
     .all()

    return [{'name': t[0], 'count': t[1]} for t in topics if t[0]]

def get_featured_news(limit=6):
    return InternationalEducation.query\
        .filter_by(is_featured=True)\
        .order_by(InternationalEducation.publish_date.desc())\
        .limit(limit)\
        .all()

def get_news_by_source(source_name):
    return InternationalEducation.query\
        .filter_by(source_name=source_name, is_featured=True)\
        .order_by(InternationalEducation.publish_date.desc())\
        .limit(10)\
        .all()

def get_latest_news_count():
    """获取最新精选新闻的数量"""
    return InternationalEducation.query.filter_by(is_featured=True).count()
