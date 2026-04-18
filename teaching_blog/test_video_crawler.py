import requests
from bs4 import BeautifulSoup
from services.video_crawler import VideoCrawler

# 测试视频爬虫
def test_video_crawler():
    crawler = VideoCrawler()
    
    # 测试B站教育频道
    print("\n=== 测试B站教育频道 ===")
    bilibili_url = "https://www.bilibili.com/v/education/"
    bilibili_html = crawler.fetch_page(bilibili_url)
    if bilibili_html:
        print(f"成功获取B站页面，长度: {len(bilibili_html)}")
        # 检查页面是否包含预期的视频卡片
        soup = BeautifulSoup(bilibili_html, 'html.parser')
        items = soup.select('div.bili-video-card')
        print(f"找到 {len(items)} 个视频卡片")
        if items:
            # 打印第一个视频卡片的HTML，查看结构
            print("\n第一个视频卡片HTML:")
            print(items[0].prettify()[:500])
        else:
            # 打印页面的部分内容，查看实际结构
            print("\n页面部分内容:")
            print(bilibili_html[:1000])
    
    # 测试土豆教育频道
    print("\n=== 测试土豆教育频道 ===")
    tudou_url = "https://www.tudou.com/list/education.html"
    tudou_html = crawler.fetch_page(tudou_url)
    if tudou_html:
        print(f"成功获取土豆网页面，长度: {len(tudou_html)}")
        soup = BeautifulSoup(tudou_html, 'html.parser')
        items = soup.select('div.item')
        print(f"找到 {len(items)} 个视频卡片")
    
    # 测试爱奇艺教育频道
    print("\n=== 测试爱奇艺教育频道 ===")
    iqiyi_url = "https://www.iqiyi.com/a_19rrhau4kp.html"
    iqiyi_html = crawler.fetch_page(iqiyi_url)
    if iqiyi_html:
        print(f"成功获取爱奇艺页面，长度: {len(iqiyi_html)}")
        soup = BeautifulSoup(iqiyi_html, 'html.parser')
        items = soup.select('div.list_item')
        print(f"找到 {len(items)} 个视频卡片")

if __name__ == "__main__":
    test_video_crawler()
