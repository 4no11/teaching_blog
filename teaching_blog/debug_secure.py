from werkzeug.utils import secure_filename

test_filenames = [
    "实验：基于多层感知器的异或门实现.docx",
    "test.docx",
    "测试文件.txt"
]

for fn in test_filenames:
    safe = secure_filename(fn)
    ext = safe.rsplit('.', 1)[-1].lower() if '.' in safe else ''
    print(f"Original: {fn}")
    print(f"  Secure:  '{safe}'")
    print(f"  Ext:     '{ext}'")
    print()
