import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_decode(content):
    if isinstance(content, str):
        return content
    if content is None:
        return ''
    if isinstance(content, bytes):
        encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'gbk', 'gb2312']
        for encoding in encodings_to_try:
            try:
                return content.decode(encoding, errors='ignore')
            except Exception:
                continue
        try:
            return content.decode('utf-8', errors='ignore')
        except Exception:
            return content.decode('latin-1', errors='ignore')
    return str(content)

class VideoCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def fetch_page(self, url, timeout=30):
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            content = response.content
            decoded_content = safe_decode(content)
            return decoded_content
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def clean_text(self, text):
        if text is None:
            return ''
        text = safe_decode(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def parse_bilibili_education(self, html):
        videos = []
        if not html:
            return videos

        soup = BeautifulSoup(html, 'html.parser')

        # 优化B站视频解析，确保获取封面图
        items = soup.select('div.bili-video-card')
        for item in items:
            try:
                title_elem = item.select_one('h3.bili-video-card__info--tit')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link_elem = item.select_one('a.bili-video-card__image-wrapper')
                if not link_elem:
                    continue
                
                href = link_elem.get('href', '')
                if href and not href.startswith('http'):
                    href = urljoin('https://www.bilibili.com/', href)
                
                # 优化封面图获取逻辑
                thumbnail_elem = item.select_one('img.bili-video-card__cover')
                thumbnail_url = ''
                if thumbnail_elem:
                    thumbnail_url = thumbnail_elem.get('src', '')
                    # 处理B站封面图URL，确保使用高清图
                    if thumbnail_url:
                        # 移除B站封面图URL中的参数，获取原始大图
                        if '?w=' in thumbnail_url:
                            thumbnail_url = thumbnail_url.split('?w=')[0]
                        # 如果没有封面图，使用默认图
                if not thumbnail_url:
                    thumbnail_url = 'https://picsum.photos/id/1005/600/338'
                
                if title and len(title) > 5:
                    videos.append({
                        'title': title,
                        'video_url': href,
                        'thumbnail_url': thumbnail_url,
                        'source_name': 'Bilibili',
                        'source_url': href,
                        'category': 'Education',
                        'publish_date': datetime.utcnow()
                    })
            except Exception as e:
                logger.error(f"Error parsing Bilibili video: {e}")
                continue

        return videos

    def parse_tudou_education(self, html):
        videos = []
        if not html:
            return videos

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('div.item')
        for item in items:
            try:
                title_elem = item.select_one('a.tit')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')
                if href and not href.startswith('http'):
                    href = urljoin('https://www.tudou.com/', href)
                
                # 优化封面图获取逻辑
                thumbnail_elem = item.select_one('img.pic')
                thumbnail_url = ''
                if thumbnail_elem:
                    thumbnail_url = thumbnail_elem.get('src', '')
                    # 处理土豆网封面图URL
                    if thumbnail_url and not thumbnail_url.startswith('http'):
                        thumbnail_url = urljoin('https://www.tudou.com/', thumbnail_url)
                # 如果没有封面图，使用默认图
                if not thumbnail_url:
                    thumbnail_url = 'https://picsum.photos/id/1006/600/338'
                
                if title and len(title) > 5:
                    videos.append({
                        'title': title,
                        'video_url': href,
                        'thumbnail_url': thumbnail_url,
                        'source_name': 'Tudou',
                        'source_url': href,
                        'category': 'Education',
                        'publish_date': datetime.utcnow()
                    })
            except Exception as e:
                logger.error(f"Error parsing Tudou video: {e}")
                continue

        return videos

    def parse_iqiyi_education(self, html):
        videos = []
        if not html:
            return videos

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('div.list_item')
        for item in items:
            try:
                title_elem = item.select_one('a.main_link')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')
                if href and not href.startswith('http'):
                    href = urljoin('https://www.iqiyi.com/', href)
                
                # 优化封面图获取逻辑
                thumbnail_elem = item.select_one('img.qy_pic_img')
                thumbnail_url = ''
                if thumbnail_elem:
                    thumbnail_url = thumbnail_elem.get('src', '')
                    # 处理爱奇艺封面图URL
                    if thumbnail_url and not thumbnail_url.startswith('http'):
                        thumbnail_url = urljoin('https://www.iqiyi.com/', thumbnail_url)
                # 如果没有封面图，使用默认图
                if not thumbnail_url:
                    thumbnail_url = 'https://picsum.photos/id/1007/600/338'
                
                if title and len(title) > 5:
                    videos.append({
                        'title': title,
                        'video_url': href,
                        'thumbnail_url': thumbnail_url,
                        'source_name': 'IQiyi',
                        'source_url': href,
                        'category': 'Education',
                        'publish_date': datetime.utcnow()
                    })
            except Exception as e:
                logger.error(f"Error parsing IQiyi video: {e}")
                continue

        return videos

    def crawl_all_sources(self):
        sources = [
            {
                'name': 'Bilibili Education',
                'url': 'https://www.bilibili.com/v/education/',
                'parser': 'parse_bilibili_education'
            },
            {
                'name': 'Tudou Education',
                'url': 'https://www.tudou.com/list/education.html',
                'parser': 'parse_tudou_education'
            },
            {
                'name': 'IQiyi Education',
                'url': 'https://www.iqiyi.com/a_19rrhau4kp.html',
                'parser': 'parse_iqiyi_education'
            }
        ]

        all_videos = []

        for source in sources:
            logger.info(f"Crawling {source['name']}...")
            try:
                html = self.fetch_page(source['url'])
                if html:
                    parser_method = getattr(self, source['parser'], None)
                    if parser_method:
                        videos = parser_method(html)
                        all_videos.extend(videos)
                        logger.info(f"Found {len(videos)} videos from {source['name']}")
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error crawling {source['name']}: {e}")

        return all_videos

class FeaturedVideoSelector:
    def select_featured(self, videos, limit=20):
        scored_videos = []
        for video in videos:
            score = 0

            keywords_high = ['教学', '教育', '学习', '课程', '教程', '知识']
            keywords_medium = ['小学', '初中', '高中', '大学', '培训', '辅导']

            title_lower = video.get('title', '').lower()
            
            for kw in keywords_high:
                if kw in title_lower:
                    score += 3

            for kw in keywords_medium:
                if kw in title_lower:
                    score += 1

            if video.get('source_name') in ['Bilibili', 'Tudou']:
                score += 2

            scored_videos.append((score, video))

        scored_videos.sort(key=lambda x: x[0], reverse=True)
        return [v[1] for v in scored_videos[:limit]]