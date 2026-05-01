"""
RAG知识库清理工具 - 删除重复或不需要的知识库
"""

import os
import json
import shutil
from datetime import datetime

# 基础目录
BASE_DIR = os.path.join(os.getcwd(), 'rag_knowledge_base')
METADATA_FILE = os.path.join(BASE_DIR, 'metadata.json')
KB_DIR = os.path.join(BASE_DIR, 'knowledge_bases')
CHROMA_DIR = os.path.join(BASE_DIR, 'chroma_db')
DOCUMENTS_DIR = os.path.join(BASE_DIR, 'documents')


def load_metadata():
    """加载元数据"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'knowledge_bases': {}}


def save_metadata(metadata):
    """保存元数据"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def list_all_knowledge_bases():
    """列出所有知识库"""
    metadata = load_metadata()
    kbs = metadata.get('knowledge_bases', {})

    print("\n" + "="*60)
    print(f"当前共有 {len(kbs)} 个知识库：")
    print("="*60)

    for i, (kb_id, info) in enumerate(kbs.items(), 1):
        print(f"\n[{i}] ID: {kb_id}")
        print(f"    名称: {info.get('name', '未知')}")
        print(f"    描述: {info.get('description', '无')}")
        print(f"    创建时间: {info.get('created_at', '未知')}")
        print(f"    文档数: {info.get('document_count', 0)}")

    return kbs


def delete_knowledge_base(kb_id):
    """删除指定知识库"""
    metadata = load_metadata()

    if kb_id not in metadata['knowledge_bases']:
        print(f"❌ 知识库不存在: {kb_id}")
        return False

    kb_info = metadata['knowledge_bases'][kb_id]
    name = kb_info.get('name', '未知')

    print(f"\n正在删除知识库: {name} (ID: {kb_id})")

    try:
        # 删除知识库目录
        if os.path.exists(kb_info.get('path', '')):
            shutil.rmtree(kb_info['path'])
            print(f"  ✅ 已删除目录: {kb_info['path']}")

        # 删除Chroma数据库
        if os.path.exists(kb_info.get('chroma_path', '')):
            shutil.rmtree(kb_info['chroma_path'])
            print(f"  ✅ 已删除向量数据库: {kb_info['chroma_path']}")

        # 删除文档目录
        doc_dir = os.path.join(DOCUMENTS_DIR, kb_id)
        if os.path.exists(doc_dir):
            shutil.rmtree(doc_dir)
            print(f"  ✅ 已删除文档目录: {doc_dir}")

        # 从元数据中移除
        del metadata['knowledge_bases'][kb_id]
        save_metadata(metadata)

        print(f"\n✅ 知识库 '{name}' 删除成功！")
        return True

    except Exception as e:
        print(f"\n❌ 删除失败: {e}")
        return False


def find_duplicates():
    """查找重复名称的知识库"""
    metadata = load_metadata()
    kbs = metadata.get('nowledge_bases', {})

    name_count = {}
    duplicates = []

    for kb_id, info in kbs.items():
        name = info.get('name', '')
        if name in name_count:
            name_count[name].append(kb_id)
            if len(name_count[name]) == 2:
                duplicates.append(name)
        else:
            name_count[name] = [kb_id]

    if duplicates:
        print("\n⚠️  发现以下重复的知识库名称：")
        for name in duplicates:
            ids = name_count[name]
            print(f"\n  名称: '{name}' ({len(ids)} 个重复)")
            for i, kb_id in enumerate(ids, 1):
                info = kbs[kb_id]
                print(f"    [{i}] ID: {kb_id} (创建于 {info.get('created_at', '未知')})")

        return duplicates
    else:
        print("\n✅ 未发现重复的知识库")
        return []


def clean_duplicates():
    """自动清理重复知识库（保留最新的）"""
    metadata = load_metadata()
    kbs = metadata.get('knowledge_bases', {})

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

    for name, group in name_groups.items():
        if len(group) > 1:
            print(f"\n发现重复: '{name}' ({len(group)} 个)")

            # 按创建时间排序（保留最新的）
            group.sort(key=lambda x: x['created_at'], reverse=True)

            # 保留第一个，删除其余
            keep = group[0]
            print(f"  保留: {keep['id']} (最新)")

            for item in group[1:]:
                kb_id = item['id']
                print(f"  删除: {kb_id}")

                try:
                    # 删除相关目录
                    if os.path.exists(item['info'].get('path', '')):
                        shutil.rmtree(item['info']['path'])
                    if os.path.exists(item['info'].get('chroma_path', '')):
                        shutil.rmtree(item['info']['chroma_path'])

                    doc_dir = os.path.join(DOCUMENTS_DIR, kb_id)
                    if os.path.exists(doc_dir):
                        shutil.rmtree(doc_dir)

                    # 从元数据中移除
                    del metadata['knowledge_bases'][kb_id]
                    deleted_count += 1

                except Exception as e:
                    print(f"    ❌ 删除失败: {e}")

    if deleted_count > 0:
        save_metadata(metadata)
        print(f"\n✅ 清理完成！共删除 {deleted_count} 个重复知识库")
    else:
        print("\n✅ 无需清理")


def main():
    """主菜单"""
    print("\n" + "="*60)
    print("       RAG 知识库管理工具")
    print("="*60)

    while True:
        print("\n请选择操作：")
        print("1. 列出所有知识库")
        print("2. 查找重复知识库")
        print("3. 自动清理重复项（保留最新的）")
        print("4. 手动删除指定知识库")
        print("5. 退出")

        choice = input("\n请输入选项 (1-5): ").strip()

        if choice == '1':
            list_all_knowledge_bases()

        elif choice == '2':
            find_duplicates()

        elif choice == '3':
            confirm = input("\n确定要自动清理重复知识库吗？(y/n): ").lower()
            if confirm == 'y':
                clean_duplicates()
            else:
                print("已取消")

        elif choice == '4':
            list_all_knowledge_bases()
            kb_id = input("\n请输入要删除的知识库ID: ").strip()
            if kb_id:
                confirm = input(f"确定要删除知识库 {kb_id} 吗？此操作不可恢复！(y/n): ").lower()
                if confirm == 'y':
                    delete_knowledge_base(kb_id)
                else:
                    print("已取消")

        elif choice == '5':
            print("\n再见！")
            break

        else:
            print("无效选项，请重新选择")

        input("\n按回车继续...")


if __name__ == '__main__':
    main()
