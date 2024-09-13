from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import DirectoryTree, Label

from clive.__private.core.constants.tui.placeholders import PATH_PLACEHOLDER
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.path_input import PathInput
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.validators.path_validator import PathValidator


class FilePathInputContainer(Horizontal):
    """Container for file path input and label."""


class DirectoryTreeHint(Label):
    """Hint for DirectoryTree widget."""


class Body(VerticalScroll, can_focus=False):
    """Container for widgets."""


class SelectFile(BaseScreen):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f2", "save", "Ok"),
    ]

    SECTION_TITLE: ClassVar[str] = "Select file"

    @dataclass
    class Saved(Message):
        """Emitted when user saves the form."""

        file_path: Path

    def __init__(
        self,
        *,
        validator_mode: PathValidator.Modes = "is_file",
        placeholder: str = PATH_PLACEHOLDER,
        notice: str | None = None,
    ) -> None:
        super().__init__()
        self._file_path_input = PathInput(placeholder=placeholder, validator_mode=validator_mode)
        self._notice = notice

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer(section_title=self.SECTION_TITLE), Body():
            if self._notice:
                yield Notice(self._notice)
            with FilePathInputContainer():
                yield self._file_path_input
            yield from self.additional_content_after_input()
            yield DirectoryTreeHint("Or select from the directory tree:")
            yield DirectoryTree(str(Path.home()))

    def additional_content_after_input(self) -> ComposeResult:
        """Override this method to add additional content before the input."""
        return []

    @on(DirectoryTree.FileSelected)
    @on(DirectoryTree.DirectorySelected)
    def update_input_path(self, event: DirectoryTree.FileSelected) -> None:
        self._file_path_input.input.value = str(event.path)

    def action_save(self) -> None:
        path = self._file_path_input.value_or_none()
        if path is None:
            return

        self._post_saved_message()
        self.app.pop_screen()

    def _post_saved_message(self) -> None:
        self.app.post_message_to_everyone(self._create_saved_message())

    def _create_saved_message(self) -> Saved:
        return self.Saved(self._file_path_input.value_or_error)  # already validated in action_save
