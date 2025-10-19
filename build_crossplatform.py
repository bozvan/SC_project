import os
import sys
import platform
import subprocess


def build_for_current_platform():
    #system = platform.system().lower()
    #arch = platform.machine()

    #print(f"Сборка для: {system} {arch}")
    system = 'darwin'

    if system == 'windows':
        name = 'SmartOrganizer-windows'
        icon = '--icon=src/assets/icon.ico' if os.path.exists('src/assets/icon.ico') else ''
        cmd = f'pyinstaller --onefile --windowed --name {name} {icon}'

    elif system == 'linux':
        name = 'SmartOrganizer-linux'
        icon = '--icon=src/assets/icon.png' if os.path.exists('src/assets/icon.png') else ''
        cmd = f'pyinstaller --onefile --name {name} {icon}'

    elif system == 'darwin':  # macOS
        name = 'SmartOrganizer-macos'
        icon = '--icon=src/assets/icon.icns' if os.path.exists('src/assets/icon.icns') else ''
        cmd = f'pyinstaller --onefile --windowed --name {name} {icon}'

    else:
        print(f"Неподдерживаемая система: {system}")
        return

    # Добавляем общие параметры
    cmd += ' --add-data "src/assets:assets"'
    cmd += ' --add-data "src/ui:ui"'
    cmd += ' --add-data "src/*.db:."'
    cmd += ' --hidden-import core --hidden-import gui --hidden-import widgets'
    cmd += ' --paths src --paths src/core --paths src/gui --paths src/widgets'
    cmd += ' src/main.py'

    print(f"Команда: {cmd}")
    os.system(cmd)


if __name__ == "__main__":
    build_for_current_platform()
