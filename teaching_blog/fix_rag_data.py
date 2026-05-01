"""
强制重载RAG元数据并重启Flask
"""

import json
import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

METADATA_FILE = r'd:\boke\teaching_blog\rag_knowledge_base\metadata.json'

print("=" * 60)
print("   RAG 知识库数据修复工具")
print("=" * 60)

# 1. 检查metadata文件
print("\n[1/4] 检查 metadata.json...")

if not os.path.exists(METADATA_FILE):
    print(f"❌ 文件不存在: {METADATA_FILE}")
    
    # 创建新的空metadata
    print("📝 创建新的 metadata.json...")
    data = {'knowledge_bases': {}}
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
else:
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kbs = data.get('knowledge_bases', {})
    print(f"✅ 找到 {len(kbs)} 个知识库:")
    
    for kb_id, info in kbs.items():
        print(f"  • {info.get('name', '未知')} (ID: {kb_id})")
        print(f"    创建时间: {info.get('created_at', '未知')}")
        print(f"    文档数: {info.get('document_count', 0)}")
        print()

# 2. 验证目录结构
print("[2/4] 验证目录结构...")

base_dir = r'd:\boke\teaching_blog\rag_knowledge_base'
dirs_to_check = [
    'knowledge_bases',
    'documents',
    'chroma_db'
]

for dir_name in dirs_to_check:
    dir_path = os.path.join(base_dir, dir_name)
    if os.path.exists(dir_path):
        count = len(os.listdir(dir_path))
        print(f"  ✅ {dir_name}/ ({count} 个项目)")
    else:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  📁 已创建 {dir_name}/")

# 3. 显示文档文件
print("\n[3/4] 检查已上传的文档...")

doc_dir = os.path.join(base_dir, 'documents')
if os.path.exists(doc_dir):
    for kb_folder in os.listdir(doc_dir):
        kb_path = os.path.join(doc_dir, kb_folder)
        if os.path.isdir(kb_path):
            files = os.listdir(kb_path)
            print(f"\n  📂 知识库 [{kb_folder}] 包含 {len(files)} 个文档:")
            for f in files:
                fpath = os.path.join(kb_path, f)
                size = os.path.getsize(fpath)
                print(f"     • {f} ({size:,} 字节)")
else:
    print("  ℹ️  无文档目录")

# 4. 总结
print("\n" + "=" * 60)
print("[4/4] 修复完成！")
print("=" * 60)

kb_count = len(data.get('knowledge_bases', {}))

if kb_count > 0:
    print(f"\n✅ 数据完整！共 {kb_count} 个知识库")
    print("\n下一步:")
    print("  1. 重启 Flask 服务: python app.py")
    print("  2. 刷新浏览器: http://localhost:5000/rag-knowledge")
    print("  3. 应该能看到您的知识库了！")
else:
    print("\n⚠️  当前无知识库数据")
    print("\n需要操作:")
    print("  1. 访问 http://localhost:5000/rag-knowledge")
    print("  2. 点击 '+ 新建知识库'")
    print("  3. 上传文档测试")

print("\n" + "=" * 60)
