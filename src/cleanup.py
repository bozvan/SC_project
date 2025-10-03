import sys
import os
from PyQt6.QtWidgets import QApplication

def cleanup_qt():
    """Принудительная очистка ресурсов PyQt"""
    app = QApplication.instance()
    if app is not None:
        print("⚠️  Принудительное завершение QApplication...")
        app.quit()
        # Даем время на освобождение ресурсов
        import time
        time.sleep(1)

if __name__ == "__main__":
    cleanup_qt()
    print("✅ Ресурсы PyQt очищены")