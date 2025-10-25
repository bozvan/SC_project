from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QInputDialog

from core.settings_manager import QtSettingsManager
from gui.ui_workspaces_widget import Ui_WorkspaceWidget
from widgets.workspace_card import WorkspaceCard


class WorkspacesWidget(QtWidgets.QWidget):
    """Виджет управления рабочими пространствами"""

    workspaceChanged = pyqtSignal(int)  # ID нового текущего workspace
    workspaceDeleted = pyqtSignal(int)  # Новый сигнал при удалении workspace

    def __init__(self, workspace_manager, current_workspace_id=1, parent=None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager
        self.settings_manager = QtSettingsManager()
        self.current_workspace_id = current_workspace_id  # Сохраняем переданный workspace
        self.workspace_cards = {}

        # Инициализация UI
        self.ui = Ui_WorkspaceWidget()
        self.ui.setupUi(self)

        # Дополнительная настройка
        self.setup_additional_ui()
        self.connect_signals()
        self.load_workspaces()

    def setup_additional_ui(self):
        """Дополнительная настройка UI элементов"""
        # Настройка кнопки создания


        # Настройка области прокрутки
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def connect_signals(self):
        """Подключает сигналы к слотам"""
        self.ui.btnCreate.clicked.connect(self.create_workspace)
        self.ui.editSearch.textChanged.connect(self.filter_workspaces)

    def load_workspaces(self):
        """Загружает список рабочих пространств"""
        # Очищаем существующие карточки
        for i in reversed(range(self.ui.gridLayoutWorkspaces.count())):
            widget = self.ui.gridLayoutWorkspaces.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.workspace_cards.clear()

        try:
            # Загружаем workspace
            workspaces = self.workspace_manager.get_all_workspaces()

            # Обновляем текущий workspace
            current_workspace = self.workspace_manager.get_workspace(self.current_workspace_id)
            if current_workspace:
                display_text = f"{current_workspace.name}"
                if current_workspace.description:
                    display_text += f" - {current_workspace.description}"
                self.ui.labelCurrentWorkspace.setText(display_text)

            # Создаем карточки
            row, col = 0, 0
            max_cols = 2

            for workspace in workspaces:
                card = WorkspaceCard(workspace)
                card.workspaceSelected.connect(self.on_workspace_selected)
                card.workspaceEditRequested.connect(self.on_workspace_edit_requested)
                card.workspaceDeleteRequested.connect(self.on_workspace_delete_requested)

                self.ui.gridLayoutWorkspaces.addWidget(card, row, col)
                self.workspace_cards[workspace.id] = card

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            # ДОБАВЛЕНО: Настройка растяжения колонок
            for i in range(max_cols):
                self.ui.gridLayoutWorkspaces.setColumnStretch(i, 1)  # Каждая колонка растягивается одинаково

            # Добавляем растягивающий элемент, чтобы карточки были прижаты к верху
            self.ui.gridLayoutWorkspaces.setRowStretch(row + 1, 1)

            # Обновляем статистику текущего workspace
            self.update_stats()

        except Exception as e:
            print(f"Ошибка при загрузке рабочих пространств: {e}")
            QtWidgets.QMessageBox.warning(self, "Ошибка",
                                          f"Не удалось загрузить рабочие пространства: {str(e)}")

    def filter_workspaces(self, search_text):
        """Фильтрует workspace по поисковому запросу"""
        search_text_lower = search_text.lower()

        for workspace_id, card in self.workspace_cards.items():
            workspace = card.workspace
            matches = (search_text_lower in workspace.name.lower() or
                       search_text_lower in (workspace.description or "").lower())
            card.setVisible(matches)

    def create_workspace(self):
        """Создает новое рабочее пространство"""
        name, ok = QtWidgets.QInputDialog.getText(
            self, "Создание рабочего пространства",
            "Введите название рабочего пространства:"
        )

        if ok and name.strip():
            description, ok = QtWidgets.QInputDialog.getText(
                self, "Описание рабочего пространства",
                "Введите описание (необязательно):"
            )

            if ok:
                try:
                    workspace = self.workspace_manager.create_workspace(
                        name.strip(),
                        description.strip() if description else ""
                    )

                    if workspace:
                        QtWidgets.QMessageBox.information(self, "Успех",
                                                          f"Рабочее пространство '{workspace.name}' создано!")
                        self.load_workspaces()
                    else:
                        QtWidgets.QMessageBox.warning(self, "Ошибка",
                                                      "Не удалось создать рабочее пространство")

                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Ошибка",
                                                  f"Ошибка при создании рабочего пространства: {str(e)}")

    def on_workspace_selected(self, workspace_id):
        """Обрабатывает выбор workspace"""
        # Обновляем текущий workspace в этом виджете
        self.current_workspace_id = workspace_id

        try:
            workspace = self.workspace_manager.get_workspace(workspace_id)

            if workspace:
                display_text = f"{workspace.name}"
                if workspace.description:
                    display_text += f" - {workspace.description}"
                self.ui.labelCurrentWorkspace.setText(display_text)

                # ДОБАВЛЕНО: Сохраняем выбранный workspace в настройках
                self.settings_manager.set_last_workspace(workspace_id)

                self.update_stats()
                # Отправляем сигнал с новым workspace_id
                self.workspaceChanged.emit(workspace_id)

                # Перезагружаем карточки, чтобы обновить подсветку
                self.load_workspaces()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка",
                                          f"Ошибка при выборе рабочего пространства: {str(e)}")

    def on_workspace_edit_requested(self, workspace_id):
        """Обрабатывает запрос на редактирование workspace"""
        try:
            workspace = self.workspace_manager.get_workspace(workspace_id)
            if not workspace or workspace.is_default:
                return

            new_name, ok = QtWidgets.QInputDialog.getText(
                self, "Редактирование рабочего пространства",
                "Введите новое название:",
                text=workspace.name
            )

            if ok and new_name.strip():
                new_description, ok = QtWidgets.QInputDialog.getText(
                    self, "Новое описание",
                    "Введите новое описание:",
                    text=workspace.description or ""
                )

                if ok:
                    success = self.workspace_manager.update_workspace(
                        workspace_id,
                        new_name.strip(),
                        new_description.strip() if new_description else ""
                    )

                    if success:
                        QtWidgets.QMessageBox.information(self, "Успех",
                                                          "Рабочее пространство обновлено!")
                        self.load_workspaces()
                    else:
                        QtWidgets.QMessageBox.warning(self, "Ошибка",
                                                      "Не удалось обновить рабочее пространство")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка",
                                          f"Ошибка при редактировании рабочего пространства: {str(e)}")

    def on_workspace_delete_requested(self, workspace_id):
        """Обрабатывает запрос на удаление workspace"""
        try:
            workspace = self.workspace_manager.get_workspace(workspace_id)
            if not workspace or workspace.is_default:
                return

            reply = QtWidgets.QMessageBox.question(
                self, "Подтверждение удаления",
                f"Вы уверены, что хотите удалить рабочее пространство '{workspace.name}'?\n"
                f"Все заметки, задачи и закладки в этом пространстве будут удалены!",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )

            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                success = self.workspace_manager.delete_workspace(workspace_id)

                if success:
                    QtWidgets.QMessageBox.information(self, "Успех",
                                                      "Рабочее пространство удалено!")

                    # Если удалили текущий workspace, переключаемся на default
                    if workspace_id == self.current_workspace_id:
                        self.current_workspace_id = 1
                        self.on_workspace_selected(1)
                    else:
                        self.load_workspaces()
                else:
                    QtWidgets.QMessageBox.warning(self, "Ошибка",
                                                  "Не удалось удалить рабочее пространство")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка",
                                          f"Ошибка при удалении рабочего пространства: {str(e)}")

    def update_stats(self):
        """Обновляет статистику текущего workspace"""
        try:
            stats = self.workspace_manager.get_workspace_stats(self.current_workspace_id)

            self.ui.labelNotes.setText(f"Заметок: {stats['notes_count']}")
            self.ui.labelTasks.setText(f"Задач: {stats['tasks_count']}")
            self.ui.labelBookmarks.setText(f"Закладок: {stats['bookmarks_count']}")
            self.ui.labelActiveTasks.setText(f"Активных задач: {stats['active_tasks_count']}")
            self.ui.labelTotal.setText(f"Всего элементов: {stats['total_items']}")

        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")
            # Устанавливаем значения по умолчанию при ошибке
            self.ui.labelNotes.setText("Заметок: 0")
            self.ui.labelTasks.setText("Задач: 0")
            self.ui.labelBookmarks.setText("Закладок: 0")
            self.ui.labelActiveTasks.setText("Активных задач: 0")
            self.ui.labelTotal.setText("Всего элементов: 0")

    def get_current_workspace_id(self):
        """Возвращает ID текущего workspace"""
        return self.current_workspace_id

    def set_current_workspace(self, workspace_id):
        """Устанавливает текущее рабочее пространство"""
        if workspace_id in self.workspace_cards:
            self.current_workspace_id = workspace_id
            self.update_current_workspace_display()
            self.update_stats()

    def update_current_workspace_display(self):
        """Обновляет отображение текущего workspace"""
        try:
            workspace = self.workspace_manager.get_workspace(self.current_workspace_id)
            if workspace:
                display_text = f"{workspace.name}"
                if workspace.description:
                    display_text += f" - {workspace.description}"
                self.ui.labelCurrentWorkspace.setText(display_text)
        except Exception as e:
            print(f"Ошибка при обновлении отображения текущего workspace: {e}")
