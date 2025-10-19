import os
import re


def fix_imports_in_file(file_path):
    """Исправляет импорты в файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Заменяем from src. на from
    old_content = content
    content = re.sub(r'from\s+src\.', 'from ', content)
    content = re.sub(r'import\s+src\.', 'import ', content)

    if old_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Исправлен: {file_path}")
        return True
    return False


def fix_all_imports():
    """Исправляет импорты во всех Python файлах"""
    folders = ['src/core', 'src/gui', 'src/widgets']

    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith('.py'):
                    file_path = os.path.join(folder, file)
                    fix_imports_in_file(file_path)


if __name__ == "__main__":
    fix_all_imports()