from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import DirectoryTree, Input, Label

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer

if TYPE_CHECKING:
    from textual.app import ComposeResult


class FilePathInputContainer(Horizontal):
    """Container for file path input and label."""


class FilePathLabel(Label):
    """Label for file path input."""


class DirectoryTreeHint(Label):
    """Hint for DirectoryTree widget."""


class Body(VerticalScroll, can_focus=False):
    """Container for widgets."""


class SelectFile(BaseScreen):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("f2", "save", "Ok"),
    ]

    _DEFAULT_PLACEHOLDER: Final[str] = "e.g.: /home/me/some-path"

    @dataclass
    class Saved(Message):
        """Emitted when user saves the form."""

        file_path: Path

    def __init__(
        self,
        default_file_path: str | None = None,
        *,
        file_must_exist: bool = True,
        placeholder: str = _DEFAULT_PLACEHOLDER,
    ) -> None:
        super().__init__()
        self.__file_must_exist = file_must_exist
        self.__file_path_input = Input(default_file_path, placeholder=placeholder)

    @property
    def file_path(self) -> Path:
        return Path(self.__file_path_input.value)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("Select file"), Body():
            with FilePathInputContainer():
                yield FilePathLabel("File path:")
                yield self.__file_path_input
            yield from self.additional_content_after_input()
            yield DirectoryTreeHint("Or select from the directory tree:")
            yield DirectoryTree(str(Path.home()))

    def additional_content_after_input(self) -> ComposeResult:
        """Override this method to add additional content before the input."""
        return []

    @on(DirectoryTree.FileSelected)
    def update_input_path(self, event: DirectoryTree.FileSelected) -> None:
        self.__file_path_input.value = str(event.path)

    def action_save(self) -> None:
        if not self.__is_valid():
            self.notify("Failed the validation process! Could not continue.", severity="error")
            return
        self._post_saved_message()
        self.app.pop_screen()

    def _post_saved_message(self) -> None:
        self.app.post_message_to_everyone(self._create_saved_message())

    def _create_saved_message(self) -> Saved:
        return self.Saved(self.file_path)

    @staticmethod
    def __is_path_valid(path: Path) -> bool:
        try:
            path.resolve()
        except (OSError, RuntimeError):
            return False
        return True

    def __is_valid(self) -> bool:
        path = self.file_path
        if self.__file_must_exist:
            return path.is_file()
        return self.__is_path_valid(path) and not path.is_dir()
