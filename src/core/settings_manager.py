# src/core/settings_manager.py
from PyQt6.QtCore import QSettings


class QtSettingsManager:
    """Менеджер настроек на основе QSettings"""

    def __init__(self, organization="SmartOrganizer", application="SmartOrganizer"):
        self.settings = QSettings(organization, application)
        print(f"⚙️ Инициализирован QSettings: {self.settings.fileName()}")

    def get_last_workspace(self) -> int:
        """Получает ID последнего рабочего пространства"""
        workspace_id = self.settings.value("last_workspace_id", 1, type=int)
        print(f"📁 Загружен последний workspace из настроек: {workspace_id}")
        return workspace_id

    def set_last_workspace(self, workspace_id: int):
        """Сохраняет ID последнего рабочего пространства"""
        self.settings.setValue("last_workspace_id", workspace_id)
        self.settings.sync()  # Принудительно сохраняем на диск
        print(f"💾 Сохранен workspace в настройки: {workspace_id}")

    def get_window_geometry(self):
        """Получает геометрию окна"""
        return self.settings.value("window_geometry")

    def set_window_geometry(self, geometry):
        """Сохраняет геометрию окна"""
        self.settings.setValue("window_geometry", geometry)

    def get_window_state(self):
        """Получает состояние окна"""
        return self.settings.value("window_state")

    def set_window_state(self, state):
        """Сохраняет состояние окна"""
        self.settings.setValue("window_state", state)

