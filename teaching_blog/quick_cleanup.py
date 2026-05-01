"""
快速清理重复知识库脚本
"""

import os
import json
import shutil
import sys

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.join(os.getcwd(), 'rag_knowledge_base')
METADATA_FILE = os.path.join(BASE_DIR, 'metadata.json')

def clean_duplicates():
    """自动清理重复知识库"""
    # 加载元数据
    if not os.path.exists(METADATA_FILE):
        print("[ERROR] 元数据文件不存在")
        return

    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    kbs = metadata.get('knowledge_bases', {})

    if not kbs:
        print("[OK] 没有知识库需要清理")
        return

    print(f"\n当前共有 {len(kbs)} 个知识库：\n")

    # 按名称分组
    name_groups = {}
    for kb_id, info in kbs.items():
        name = info.get('name', '')
        if name not in name_groups:
            name_groups[name] = []
        name_groups[name].append({
            'id': kb_id,
            'created_at': info.get('created_at', ''),
            'info': info
        })

    deleted_count = 0
    documents_dir = os.path.join(BASE_DIR, 'documents')

    for name, group in name_groups.items():
        if len(group) > 1:
            print(f"[WARN] 发现重复: '{name}' ({len(group)} 个)")

            # 按创建时间排序（保留最新的）
            group.sort(key=lambda x: x['created_at'], reverse=True)

            # 保留第一个，删除其余
            keep = group[0]
            print(f"   [KEEP] 保留: {keep['id']} (最新)")

            for item in group[1:]:
                kb_id = item['id']
                print(f"   [DEL] 删除: {kb_id}")

                try:
                    # 删除知识库目录
                    if os.path.exists(item['info'].get('path', '')):
                        shutil.rmtree(item['info']['path'])

                    # 删除Chroma数据库
                    if os.path.exists(item['info'].get('chroma_path', '')):
                        shutil.rmtree(item['info']['chroma_path'])

                    # 删除文档目录
                    doc_dir = os.path.join(documents_dir, kb_id)
                    if os.path.exists(doc_dir):
                        shutil.rmtree(doc_dir)

                    # 从元数据中移除
                    del metadata['knowledge_bases'][kb_id]
                    deleted_count += 1

                except Exception as e:
                    print(f"      [FAIL] 删除失败: {e}")

    if deleted_count > 0:
        # 保存元数据
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] 清理完成！共删除 {deleted_count} 个重复知识库")
        print(f"   剩余 {len(metadata['knowledge_bases'])} 个知识库\n")
    else:
        print("\n[OK] 无需清理，没有发现重复项\n")


if __name__ == '__main__':
    print("="*50)
    print("   RAG 知识库重复项清理工具")
    print("="*50)

    clean_duplicates()

