from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Grid
from textual.message import Message
from textual.widgets import DirectoryTree, Input, Static

from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult


class FilePathLabel(Static):
    """Label for file path input."""


class DirectoryTreeHint(Static):
    """Hint for DirectoryTree widget."""


class Body(Grid):
    """Container for widgets."""


class SelectFile(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "save", "Ok"),
    ]

    class Saved(Message):
        """Emitted when user saves the form."""

        def __init__(self, file_path: Path) -> None:
            self.file_path = file_path
            super().__init__()

    def __init__(self, default_file_path: str | None = None, *, file_must_exist: bool = True) -> None:
        super().__init__()
        self.__file_must_exist = file_must_exist
        self.__file_path_input = Input(default_file_path, placeholder="e.g.: /home/me/my-active-key")

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("Select file"), Body():
            yield FilePathLabel("File path:")
            yield self.__file_path_input
            yield DirectoryTreeHint("Or select from the directory tree:")
            yield DirectoryTree(str(Path.home()))

    @on(DirectoryTree.FileSelected)
    def update_input_path(self, event: DirectoryTree.FileSelected) -> None:
        self.__file_path_input.value = str(event.path)

    def action_save(self) -> None:
        if not self.__is_valid():
            Notification("Failed the validation process! Could not continue.", category="error").show()
            return
        self.app.post_message_to_everyone(self.Saved(self.__get_file_path()))
        self.app.pop_screen()

    def __is_valid(self) -> bool:
        if self.__file_must_exist:
            return self.__get_file_path().is_file()
        return True

    def __get_file_path(self) -> Path:
        return Path(self.__file_path_input.value)
