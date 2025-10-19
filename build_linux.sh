#!/bin/bash
echo "Установка зависимостей..."
pip3 install -r src/requirements.txt

echo "Сборка приложения..."
pyinstaller smart_organizer.spec

echo "Копирование дополнительных файлов..."
cp src/*.db dist/ 2>/dev/null || true

echo "Установка прав выполнения..."
chmod +x dist/SmartOrganizer

echo "Сборка завершена!"