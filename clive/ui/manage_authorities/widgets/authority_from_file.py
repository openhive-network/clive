from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.message import Message
from textual.widgets import DirectoryTree, Input, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.dialog_container import DialogContainer
from clive.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult


class FilePathLabel(Static):
    """Label for file path input"""


class DirectoryTreeHint(Static):
    """Hint for DirectoryTree widget"""


class AuthorityFromFile(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f10", "save", "Save"),
    ]

    class Saved(Message):
        """Emitted when user saves the form"""

        def __init__(self, file_path: Path) -> None:
            self.file_path = file_path
            super().__init__()

    def __init__(self, default_file_path: str | None = None) -> None:
        super().__init__()
        self.__file_path_input = Input(default_file_path, placeholder="e.g.: /home/me/my-active-key")

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield FilePathLabel("Authority file path:")
            yield self.__file_path_input
            yield DirectoryTreeHint("Or select from the directory tree:")
            yield DirectoryTree(str(Path.home()))

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.__file_path_input.value = event.path

    def action_save(self) -> None:
        if not self.__is_valid():
            Notification("Failed the validation process! Could not continue.", category="error").show()
            return
        self.app.post_message_to_everyone(self.Saved(self.__get_file_path()))
        self.app.pop_screen()

    def __is_valid(self) -> bool:
        return self.__get_file_path().is_file()

    def __get_file_path(self) -> Path:
        return Path(self.__file_path_input.value)
