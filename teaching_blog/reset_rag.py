"""
完全重置RAG知识库 - 删除所有数据和元数据
"""

import os
import json
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.join(os.getcwd(), 'rag_knowledge_base')
METADATA_FILE = os.path.join(BASE_DIR, 'metadata.json')

def reset_all():
    """完全重置所有知识库数据"""
    print("="*50)
    print("   RAG 知识库完全重置工具")
    print("="*50)

    # 加载现有元数据
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        kbs = metadata.get('knowledge_bases', {})
        count = len(kbs)

        if count > 0:
            print(f"\n[INFO] 发现 {count} 个知识库，准备删除...\n")

            for kb_id, info in kbs.items():
                name = info.get('name', '未知')
                print(f"[DEL] 删除: {name} (ID: {kb_id})")

                try:
                    # 删除知识库目录
                    if os.path.exists(info.get('path', '')):
                        shutil.rmtree(info['path'])

                    # 删除Chroma数据库
                    if os.path.exists(info.get('chroma_path', '')):
                        shutil.rmtree(info['chroma_path'])

                except Exception as e:
                    print(f"      [WARN] 删除目录失败: {e}")

            # 删除文档目录
            documents_dir = os.path.join(BASE_DIR, 'documents')
            if os.path.exists(documents_dir):
                shutil.rmtree(documents_dir)
                print("[DEL] 已删除所有文档")

            # 重置元数据为空
            metadata = {'knowledge_bases': {}}
            with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"\n[OK] 重置完成！已删除 {count} 个知识库")
            print("   现在可以重新创建知识库了\n")
        else:
            print("\n[OK] 已经是空的了，无需重置\n")
    else:
        print("\n[OK] 元数据文件不存在，无需重置\n")


if __name__ == '__main__':
    reset_all()
