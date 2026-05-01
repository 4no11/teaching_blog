"""
诊断文档加载问题 - 直接测试TextLoader
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 测试文件路径
test_file = r'd:\boke\teaching_blog\rag_knowledge_base\documents\20260501172221_爬虫\test_document.txt'

print("=" * 60)
print("   文档加载诊断工具")
print("=" * 60)

# 1. 检查文件是否存在
print(f"\n[1/5] 检查文件是否存在...")
if not os.path.exists(test_file):
    print(f"❌ 文件不存在: {test_file}")
    sys.exit(1)

print(f"✅ 文件存在: {test_file}")

# 2. 检查文件大小
print(f"\n[2/5] 检查文件大小...")
file_size = os.path.getsize(test_file)
print(f"📊 文件大小: {file_size:,} 字节 ({file_size} bytes)")

if file_size == 0:
    print("❌ 文件为空！")
    sys.exit(1)

# 3. 尝试读取原始内容
print(f"\n[3/5] 尝试读取原始内容...")

encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp1252']

content = None
used_encoding = None

for encoding in encodings_to_try:
    try:
        with open(test_file, 'r', encoding=encoding) as f:
            content = f.read()
            used_encoding = encoding
        print(f"✅ 成功使用编码 [{encoding}] 读取")
        print(f"\n📄 内容预览 (前200字符):")
        print("-" * 40)
        print(content[:200])
        print("-" * 40)
        break
    except UnicodeDecodeError as e:
        print(f"⚠️  编码 [{encoding}] 失败: {e}")
        continue
    except Exception as e:
        print(f"❌ 其他错误 [{encoding}]: {e}")

if content is None:
    print("\n❌ 所有编码都失败！无法读取文件")
    sys.exit(1)

# 4. 测试LangChain TextLoader
print(f"\n[4/5] 测试 LangChain TextLoader...")

try:
    from langchain_community.document_loaders import TextLoader

    # 使用成功读取的编码
    loader = TextLoader(test_file, encoding=used_encoding)
    documents = loader.load()

    if documents:
        print(f"✅ TextLoader 成功！加载了 {len(documents)} 个文档")
        for i, doc in enumerate(documents):
            print(f"\n   文档 {i+1}:")
            print(f"   - 页面内容长度: {len(doc.page_content)} 字符")
            print(f"   - 元数据: {doc.metadata}")
            if doc.page_content:
                print(f"   - 内容预览: {doc.page_content[:100]}...")
    else:
        print("⚠️  TextLoader 返回空列表")

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请安装: pip install langchain-community")
except Exception as e:
    print(f"❌ TextLoader 失败: {e}")
    import traceback
    print(f"详细错误:\n{traceback.format_exc()}")

# 5. 总结
print(f"\n{'=' * 60}")
print("[5/5] 诊断总结:")
print(f"{'=' * 60}")
print(f"✅ 文件存在且非空")
print(f"✅ 可用编码: {used_encoding}")
print(f"✅ 原始读取: 成功 ({len(content)} 字符)")

if content and len(content) > 0:
    print(f"\n🎉 结论: 文件正常，问题可能在Flask服务未使用最新代码")
    print(f"\n建议操作:")
    print(f"  1. 重启 Flask 服务 (Ctrl+C → python app.py)")
    print(f"  2. 清除浏览器缓存 (Ctrl+Shift+Delete)")
    print(f"  3. 强制刷新页面 (Ctrl+F5)")
else:
    print(f"\n❌ 结论: 文件内容异常")
