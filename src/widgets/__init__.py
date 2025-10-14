"""
Виджеты для Умного Органайзера
"""

from .rich_text_editor import RichTextEditor
from .tags_widget import TagsWidget
from .task_widget import TaskWidget
from .tasks_editor import TasksEditor
from .workspace_card import WorkspaceCard
from .workspaces_widget import WorkspacesWidget
from .bookmark_item_widget import BookmarkItemWidget
from .bookmarks_widget import BookmarksWidget

__all__ = ['RichTextEditor', 'TagsWidget', 'TaskWidget', 'TasksEditor', 'WorkspaceCard', 'WorkspacesWidget',
           'BookmarkItemWidget', 'BookmarksWidget']
