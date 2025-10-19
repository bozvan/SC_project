@echo off
echo Установка зависимостей...
pip install -r src/requirements.txt

echo Сборка приложения...
pyinstaller smart_organizer.spec

echo Копирование дополнительных файлов...
if exist "src\*.db" copy "src\*.db" "dist\"

echo Сборка завершена!
pause