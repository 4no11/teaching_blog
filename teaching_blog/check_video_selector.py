import requests
from bs4 import BeautifulSoup

# 检查土豆网教育频道的实际页面结构
def check_tudou_selector():
    url = "https://www.tudou.com/list/education.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("=== 土豆网教育频道结构检查 ===")
        print(f"页面状态码: {response.status_code}")
        print(f"页面标题: {soup.title.text}")
        
        # 查找可能的视频容器
        print("\n查找可能的视频容器:")
        divs = soup.find_all('div', limit=20)
        for div in divs:
            # 查找包含视频相关关键词的div
            if 'video' in str(div).lower() or 'item' in div.get('class', []) or 'list' in div.get('class', []):
                print(f"\nDiv类名: {div.get('class')}")
                print(f"Div ID: {div.get('id')}")
                print(f"Div HTML (前300字符): {str(div)[:300]}")
        
        # 查找所有a标签
        print("\n查找所有a标签 (前10个):")
        a_tags = soup.find_all('a', limit=10)
        for a in a_tags:
            href = a.get('href', '')
            if 'video' in href or 'item' in href:
                print(f"A标签: {a.text.strip()}")
                print(f"链接: {href}")

# 检查爱奇艺教育频道的实际页面结构
def check_iqiyi_selector():
    url = "https://www.iqiyi.com/a_19rrhau4kp.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n=== 爱奇艺教育频道结构检查 ===")
        print(f"页面状态码: {response.status_code}")
        print(f"页面标题: {soup.title.text}")
        
        # 查找可能的视频容器
        print("\n查找可能的视频容器:")
        divs = soup.find_all('div', limit=20)
        for div in divs:
            # 查找包含视频相关关键词的div
            if 'video' in str(div).lower() or 'item' in div.get('class', []) or 'list' in div.get('class', []):
                print(f"\nDiv类名: {div.get('class')}")
                print(f"Div ID: {div.get('id')}")
                print(f"Div HTML (前300字符): {str(div)[:300]}")
        
        # 查找所有a标签
        print("\n查找所有a标签 (前10个):")
        a_tags = soup.find_all('a', limit=10)
        for a in a_tags:
            href = a.get('href', '')
            if 'video' in href or 'item' in href:
                print(f"A标签: {a.text.strip()}")
                print(f"链接: {href}")

if __name__ == "__main__":
    check_tudou_selector()
    check_iqiyi_selector()
