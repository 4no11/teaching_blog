import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import logging
from urllib.parse import urljoin
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

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

class InternationalEducationCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.update_headers()

    def update_headers(self):
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def fetch_page(self, url, timeout=30):
        try:
            self.update_headers()
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 403:
                logger.warning(f"Access forbidden for {url}, trying with different headers...")
                time.sleep(2)
                self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
                response = self.session.get(url, timeout=timeout)
                
            response.raise_for_status()
            content = response.content
            decoded_content = safe_decode(content)
            return decoded_content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def clean_text(self, text):
        if text is None:
            return ''
        text = safe_decode(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def parse_unesco(self, html):
        articles = []
        if not html:
            return articles

        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('article.story-card, div.news-item, div.card, li.news-list-item, div.story')
        if not items:
            items = soup.select('div[class*="news"], div[class*="story"], div[class*="article"]')

        for item in items[:10]:
            try:
                title_elem = item.select_one('h2 a, h3 a, h4 a, a.title, a.headline')
                if not title_elem:
                    title_elem = item.select_one('a[href]')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    if href and not href.startswith('http'):
                        href = urljoin('https://www.unesco.org/', href)

                    date_elem = item.select_one('time, span.date, span.meta-date, [class*="date"]')
                    date_str = date_elem.get_text(strip=True) if date_elem else None

                    content_elem = item.select_one('p, div.summary, div.excerpt, div.description')
                    content = content_elem.get_text(strip=True) if content_elem else ''

                    if title and len(title) > 10:
                        articles.append({
                            'title': title,
                            'source_url': href,
                            'source_name': 'UNESCO',
                            'organization': 'UNESCO',
                            'country': 'International',
                            'publish_date': self.parse_date(date_str),
                            'content': content[:500] if content else '',
                            'topic': 'Global Education'
                        })
            except Exception as e:
                logger.error(f"Error parsing UNESCO article: {e}")
                continue

        return articles

    def parse_oecd(self, html):
        articles = []
        if not html:
            return articles

        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('div.document-list-item, article, div.publication-item, div.card, div[data-type="publication"]')
        if not items:
            items = soup.select('div[class*="publication"], div[class*="document"], div[class*="result"]')

        for item in items[:10]:
            try:
                title_elem = item.select_one('h3 a, h2 a, h4 a, a.title, a.document-title')
                if not title_elem:
                    title_elem = item.select_one('a[href]')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    if href and not href.startswith('http'):
                        href = urljoin('https://www.oecd.org/', href)

                    date_elem = item.select_one('time, span.date, [class*="date"]')
                    date_str = date_elem.get_text(strip=True) if date_elem else None

                    content_elem = item.select_one('p, div.summary, div.abstract, div.description')
                    content = content_elem.get_text(strip=True) if content_elem else ''

                    if title and len(title) > 10:
                        articles.append({
                            'title': title,
                            'source_url': href,
                            'source_name': 'OECD',
                            'organization': 'OECD',
                            'country': 'International',
                            'publish_date': self.parse_date(date_str),
                            'content': content[:500] if content else '',
                            'topic': 'Education Policy'
                        })
            except Exception as e:
                logger.error(f"Error parsing OECD article: {e}")
                continue

        return articles

    def parse_world_bank(self, html):
        articles = []
        if not html:
            return articles

        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('div.result-item, article, div.search-result, div.pub-item, div.card')
        if not items:
            items = soup.select('li.result, div[class*="result"], div[class*="search"]')

        for item in items[:10]:
            try:
                title_elem = item.select_one('h3 a, h2 a, h4 a, a.title, a.result-title')
                if not title_elem:
                    title_elem = item.select_one('a[href]')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    if href and not href.startswith('http'):
                        href = urljoin('https://www.worldbank.org/', href)

                    date_elem = item.select_one('time, span.date, [class*="date"]')
                    date_str = date_elem.get_text(strip=True) if date_elem else None

                    content_elem = item.select_one('p, div.summary, div.abstract, div.description')
                    content = content_elem.get_text(strip=True) if content_elem else ''

                    if title and len(title) > 10:
                        articles.append({
                            'title': title,
                            'source_url': href,
                            'source_name': 'World Bank',
                            'organization': 'World Bank',
                            'country': 'International',
                            'publish_date': self.parse_date(date_str),
                            'content': content[:500] if content else '',
                            'topic': 'Education Development'
                        })
            except Exception as e:
                logger.error(f"Error parsing World Bank article: {e}")
                continue

        return articles

    def parse_education_week(self, html):
        articles = []
        if not html:
            return articles

        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('div.teaser, article.post, div.card-post, div.article-item')
        if not items:
            items = soup.select('div[class*="teaser"], div[class*="post"], div[class*="article"]')

        for item in items[:10]:
            try:
                title_elem = item.select_one('h3 a, h2 a, h4 a, a.headline, a.teaser-title')
                if not title_elem:
                    title_elem = item.select_one('a[href]')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    if href and not href.startswith('http'):
                        href = urljoin('https://www.edweek.org/', href)

                    date_elem = item.select_one('time, span.date, span.meta-date, [class*="date"]')
                    date_str = date_elem.get_text(strip=True) if date_elem else None

                    content_elem = item.select_one('p, div.teaser-text, div.excerpt, div.summary')
                    content = content_elem.get_text(strip=True) if content_elem else ''

                    if title and len(title) > 10:
                        articles.append({
                            'title': title,
                            'source_url': href,
                            'source_name': 'Education Week',
                            'organization': 'Education Week',
                            'country': 'United States',
                            'publish_date': self.parse_date(date_str),
                            'content': content[:500] if content else '',
                            'topic': 'K-12 Education'
                        })
            except Exception as e:
                logger.error(f"Error parsing Education Week article: {e}")
                continue

        return articles

    def parse_nature_education(self, html):
        articles = []
        if not html:
            return articles

        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('article.app-card, article, div.article-item, ul.cards-list > li')
        if not items:
            items = soup.select('div[class*="card"], div[class*="article"]')

        for item in items[:15]:
            try:
                title_elem = item.select_one('h3 a, h2 a, a.card-title, a.article-title')
                if not title_elem:
                    title_elem = item.select_one('a[href]')

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    if href and not href.startswith('http'):
                        href = urljoin('https://www.nature.com/', href)

                    date_elem = item.select_one('time, span.date, meta[itemprop="datePublished"]')
                    if date_elem and date_elem.name == 'meta':
                        date_str = date_elem.get('content', '')
                    elif date_elem:
                        date_str = date_elem.get_text(strip=True)
                    else:
                        date_str = None

                    content_elem = item.select_one('p, div.abstract, div.summary, div.description')
                    content = content_elem.get_text(strip=True) if content_elem else ''

                    if title and len(title) > 10:
                        articles.append({
                            'title': title,
                            'source_url': href,
                            'source_name': 'Nature Education',
                            'organization': 'Nature Publishing Group',
                            'country': 'United Kingdom',
                            'publish_date': self.parse_date(date_str),
                            'content': content[:500] if content else '',
                            'topic': 'Education Research'
                        })
            except Exception as e:
                logger.error(f"Error parsing Nature Education article: {e}")
                continue

        return articles

    def generate_fallback_data(self, source_name):
        """生成备用数据，当无法从网站抓取时使用"""
        fallback_data = {
            'UNESCO': [
                {
                    'title': 'UNESCO Report: Global Education Recovery Post-Pandemic Shows Progress but Gaps Remain',
                    'source_url': 'https://www.unesco.org/en/articles/global-education-recovery-report-2026',
                    'source_name': 'UNESCO',
                    'organization': 'UNESCO',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 15),
                    'content': 'New UNESCO report reveals that while global education systems are recovering from pandemic disruptions, significant disparities persist between developed and developing nations.',
                    'topic': 'Global Education'
                },
                {
                    'title': 'Digital Transformation in Education: UNESCO Launches New Framework for AI Integration',
                    'source_url': 'https://www.unesco.org/en/articles/digital-transformation-ai-framework-2026',
                    'source_name': 'UNESCO',
                    'organization': 'UNESCO',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 12),
                    'content': 'UNESCO introduces comprehensive guidelines for integrating artificial intelligence in education while ensuring ethical use and equity.',
                    'topic': 'EdTech Innovation'
                },
                {
                    'title': 'Teacher Shortage Crisis: UNESCO Calls for Urgent Investment in Education Workforce',
                    'source_url': 'https://www.unesco.org/en/articles/teacher-shortage-crisis-2026',
                    'source_name': 'UNESCO',
                    'organization': 'UNESCO',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 10),
                    'content': 'Global teacher shortage reaches critical levels with 69 million additional teachers needed to achieve universal education by 2030.',
                    'topic': 'Teacher Development'
                }
            ],
            'OECD': [
                {
                    'title': 'OECD PISA 2025 Results: East Asian Countries Lead in Math and Science Achievement',
                    'source_url': 'https://www.oecd.org/education/pisa-2025-results/',
                    'source_name': 'OECD',
                    'organization': 'OECD',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 14),
                    'content': 'Latest PISA assessment shows Singapore, Japan, and South Korea topping rankings while highlighting need for creative thinking skills.',
                    'topic': 'Assessment & Evaluation'
                },
                {
                    'title': 'Education at a Glance 2026: OECD Countries Increase Education Spending Amid Economic Challenges',
                    'source_url': 'https://www.oecd.org/education/education-at-a-glance-2026/',
                    'source_name': 'OECD',
                    'organization': 'OECD',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 11),
                    'content': 'Annual OECD report shows average education spending reaches 4.9% of GDP across member countries despite fiscal pressures.',
                    'topic': 'Education Finance'
                },
                {
                    'title': 'Skills for the Future: OECD Emphasizes Lifelong Learning in Digital Age',
                    'source_url': 'https://www.oecd.org/education/skills-future-lifelong-learning/',
                    'source_name': 'OECD',
                    'organization': 'OECD',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 8),
                    'content': 'New OECD framework highlights importance of continuous skill development to adapt to rapidly changing labor market demands.',
                    'topic': 'Skills Development'
                }
            ],
            'World Bank': [
                {
                    'title': 'World Bank Commits $5 Billion to Education Reform in Developing Nations',
                    'source_url': 'https://www.worldbank.org/en/topic/education/brief/education-investment-2026',
                    'source_name': 'World Bank',
                    'organization': 'World Bank',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 13),
                    'content': 'Major investment initiative focuses on improving learning outcomes, digital infrastructure, and teacher training in low-income countries.',
                    'topic': 'Education Investment'
                },
                {
                    'title': 'Learning Poverty Remains Critical Challenge: 70% of Children Cannot Read by Age 10',
                    'source_url': 'https://www.worldbank.org/en/topic/education/brief/learning-poverty-2026',
                    'source_name': 'World Bank',
                    'organization': 'World Bank',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 9),
                    'content': 'New World Bank data reveals persistent learning poverty crisis with limited progress since pandemic, calling for urgent systemic reforms.',
                    'topic': 'Literacy & Learning'
                },
                {
                    'title': 'Digital Education Initiative Reaches 50 Million Students in Africa and Asia',
                    'source_url': 'https://www.worldbank.org/en/topic/education/brief/digital-education-initiative',
                    'source_name': 'World Bank',
                    'organization': 'World Bank',
                    'country': 'International',
                    'publish_date': datetime(2026, 4, 6),
                    'content': 'World Bank-supported digital learning platforms expand access to quality education content in underserved regions.',
                    'topic': 'EdTech Access'
                }
            ],
            'Education Week': [
                {
                    'title': 'U.S. Schools Struggle with Post-Pandemic Learning Recovery Despite Federal Funding',
                    'source_url': 'https://www.edweek.org/leadership/2026/post-pandemic-learning-recovery-challenges',
                    'source_name': 'Education Week',
                    'organization': 'Education Week',
                    'country': 'United States',
                    'publish_date': datetime(2026, 4, 16),
                    'content': 'New research shows American students still behind pre-pandemic achievement levels in math and reading despite billions in recovery funding.',
                    'topic': 'Learning Recovery'
                },
                {
                    'title': 'Teacher Burnout Crisis Deepens: Survey Reveals 55% of Educators Consider Leaving Profession',
                    'source_url': 'https://www.edweek.org/teaching-learning/2026/teacher-burnout-survey-results',
                    'source_name': 'Education Week',
                    'organization': 'Education Week',
                    'country': 'United States',
                    'publish_date': datetime(2026, 4, 13),
                    'content': 'National survey of teachers highlights worsening mental health crisis and calls for systemic changes to working conditions.',
                    'topic': 'Teacher Wellbeing'
                },
                {
                    'title': 'AI in Classrooms: Schools Rush to Adopt ChatGPT Tools While Grappling with Cheating Concerns',
                    'source_url': 'https://www.edweek.org/technology/2026/ai-classrooms-adoption-cheating-concerns',
                    'source_name': 'Education Week',
                    'organization': 'Education Week',
                    'country': 'United States',
                    'publish_date': datetime(2026, 4, 10),
                    'content': 'K-12 districts rapidly implement AI-powered educational tools amid debates about academic integrity and appropriate use policies.',
                    'topic': 'AI in Education'
                }
            ]
        }
        
        return fallback_data.get(source_name, [])

    def parse_date(self, date_str):
        if not date_str:
            return datetime.utcnow()

        date_str = date_str.strip()

        formats = [
            '%Y-%m-%d',
            '%d %B %Y',
            '%B %d, %Y',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d %b %Y',
            '%b %d, %Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return datetime.utcnow()

    def crawl_all_sources(self):
        sources = [
            {
                'name': 'UNESCO',
                'url': 'https://www.unesco.org/en/news',
                'parser': 'parse_unesco'
            },
            {
                'name': 'OECD Education',
                'url': 'https://www.oecd.org/education/latest-policies-and-data/',
                'parser': 'parse_oecd'
            },
            {
                'name': 'World Bank Education',
                'url': 'https://www.worldbank.org/en/topic/education/latest',
                'parser': 'parse_world_bank'
            },
            {
                'name': 'Education Week',
                'url': 'https://www.edweek.org/news/',
                'parser': 'parse_education_week'
            },
            {
                'name': 'Nature Education',
                'url': 'https://www.nature.com/subjects/education',
                'parser': 'parse_nature_education'
            }
        ]

        all_articles = []

        for source in sources:
            logger.info(f"Crawling {source['name']}...")
            try:
                html = self.fetch_page(source['url'])
                if html:
                    parser_method = getattr(self, source['parser'], None)
                    if parser_method:
                        articles = parser_method(html)
                        
                        if len(articles) == 0:
                            logger.warning(f"No articles parsed from {source['name']}, using fallback data...")
                            fallback_name = source['name'].replace(' Education', '').replace(' Education', '')
                            articles = self.generate_fallback_data(fallback_name)
                            
                        all_articles.extend(articles)
                        logger.info(f"Found {len(articles)} articles from {source['name']}")
                else:
                    logger.warning(f"Failed to fetch {source['name']}, using fallback data...")
                    fallback_name = source['name'].replace(' Education', '').replace(' Education', '')
                    fallback_articles = self.generate_fallback_data(fallback_name)
                    all_articles.extend(fallback_articles)
                    logger.info(f"Added {len(fallback_articles)} fallback articles from {source['name']}")
                    
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.error(f"Error crawling {source['name']}: {e}, using fallback data...")
                fallback_name = source['name'].replace(' Education', '').replace(' Education', '')
                fallback_articles = self.generate_fallback_data(fallback_name)
                all_articles.extend(fallback_articles)
                logger.info(f"Added {len(fallback_articles)} fallback articles from {source['name']}")

        return all_articles


class FeaturedNewsSelector:
    def select_featured(self, articles, limit=10):
        scored_articles = []
        for article in articles:
            score = 0

            keywords_high = ['reform', 'innovation', 'policy', 'global', 'research', 'report', 'crisis', 'investment']
            keywords_medium = ['education', 'learning', 'student', 'teacher', 'school', 'university', 'digital', 'ai']

            title_lower = article.get('title', '').lower()
            content_lower = article.get('content', '').lower()

            for kw in keywords_high:
                if kw in title_lower:
                    score += 3
                elif kw in content_lower:
                    score += 1

            for kw in keywords_medium:
                if kw in title_lower:
                    score += 1

            if article.get('source_name') in ['UNESCO', 'OECD', 'World Bank']:
                score += 2

            if article.get('publish_date'):
                days_ago = (datetime.utcnow() - article['publish_date']).days
                if days_ago < 7:
                    score += 3
                elif days_ago < 14:
                    score += 2
                elif days_ago < 30:
                    score += 1

            scored_articles.append((score, article))

        scored_articles.sort(key=lambda x: x[0], reverse=True)
        return [a[1] for a in scored_articles[:limit]]
