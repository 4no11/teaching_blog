import os
import requests

WENXIN_AK = os.environ.get('WENXIN_AK', '')
WENXIN_SK = os.environ.get('WENXIN_SK', '')

print(f"AK: {WENXIN_AK}")
print(f"SK: {WENXIN_SK}")
print()

if not WENXIN_AK or not WENXIN_SK:
    print("❌ 错误：环境变量未设置")
    exit(1)

url = 'https://aip.baidubce.com/oauth/2.0/token'
params = {
    'grant_type': 'client_credentials',
    'client_id': WENXIN_AK,
    'client_secret': WENXIN_SK
}

print("正在请求 access_token...")
response = requests.post(url, params=params, timeout=10)
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
