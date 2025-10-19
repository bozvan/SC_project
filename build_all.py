#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def build_exe():
    """Сборка EXE"""
    system = platform.system().lower()
    print(f"Сборка EXE для {system}...")

    # Удаляем предыдущую сборку
    if Path('dist').exists():
        shutil.rmtree('dist')
    if Path('build').exists():
        shutil.rmtree('build')

    # Запускаем PyInstaller
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', 'smart_organizer.spec'], check=True)

        # Копируем базы данных
        for db_file in Path('src').glob('*.db'):
            shutil.copy2(db_file, 'dist')

        print(f"Сборка EXE завершена! Файлы в папке 'dist/'")

    except subprocess.CalledProcessError as e:
        print(f"Ошибка сборки: {e}")


def build_apk():
    """Сборка APK (требуется настройка Buildozer)"""
    print("Сборка APK...")
    print("Для сборки APK необходимо:")
    print("1. Установить Buildozer: pip install buildozer")
    print("2. Настроить buildozer.spec")
    print("3. Убедиться что приложение совместимо с Android")

    # Если используете Kivy вместо PyQt6
    # subprocess.run(['buildozer', 'android', 'debug'], check=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'exe':
            build_exe()
        elif sys.argv[1] == 'apk':
            build_apk()
        else:
            print("Использование: python build_all.py [exe|apk]")
    else:
        build_exe()
