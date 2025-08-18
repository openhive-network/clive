from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, VerticalGroup
from textual.reactive import reactive
from textual.widgets import DirectoryTree, Label

from clive.__private.core.constants.tui.placeholders import FILE_NAME_PLACEHOLDER
from clive.__private.core.formatters.humanize import humanize_relative_or_whole_path
from clive.__private.settings import safe_settings
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog, CliveActionDialogResultT
from clive.__private.ui.widgets.buttons.confirm_button import ConfirmOneLineButton
from clive.__private.ui.widgets.inputs.file_name_input import FileNameInput
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult

    from clive.__private.validators.file_path_validator import FilePathValidator


class FileNameInputContainer(Horizontal):
    """Container for file name input and label."""


class DirectoryTreeHint(Label):
    """Hint for DirectoryTree widget."""


class PathDisplay(VerticalGroup):
    """
    Label for displaying path.

    Attributes:
        DEFAULT_CSS: Default CSS styles for the widget.
        path: The path to display in the label.

    Args:
        path: The path to display in the label.
    """

    DEFAULT_CSS = """
        PathDisplay {

            #path {
                width: 1fr;
                text-overflow: ellipsis;
            }
        }
    """

    path: str = reactive(None, recompose=True, init=False)  # type: ignore[assignment]

    def __init__(self, path: str) -> None:
        super().__init__()
        self.set_reactive(self.__class__.path, path)  # type: ignore[arg-type]

    def compose(self) -> ComposeResult:
        yield Label("Path:")
        yield Label(self.path, id="path")


class SelectFileBaseDialog(CliveActionDialog[CliveActionDialogResultT], ABC):
    DEFAULT_CSS = """
    SelectFileBaseDialog {
        CliveDialogContent {
            width: 70%;
            height: 90%;

            FileNameInputContainer {
                height: auto;
            }

            DirectoryTreeHint {
                color: $text-muted;
            }

            DirectoryTree {
                min-height: 3;
            }

            Notice {
                margin-bottom: 1;
            }
        }
    }
    """

    def __init__(
        self,
        border_title: str,
        confirm_button_label: str = ConfirmOneLineButton.DEFAULT_LABEL,
        notice: str | None = None,
    ) -> None:
        super().__init__(border_title=border_title, confirm_button_label=confirm_button_label)
        self._notice = notice

    @property
    def _file_name_input(self) -> FileNameInput:
        return self.query_exactly_one(FileNameInput)

    @property
    def _path_display(self) -> PathDisplay:
        return self.query_exactly_one(PathDisplay)

    @property
    def _select_file_root_path(self) -> Path:
        return safe_settings.select_file_root_path

    def create_dialog_content(self) -> ComposeResult:
        if self._notice:
            yield Notice(self._notice)
        with FileNameInputContainer():
            yield PathDisplay(
                humanize_relative_or_whole_path(
                    self._select_file_root_path, self._select_file_root_path, add_trailing_slash=True
                )
            )
            yield FileNameInput(
                root_directory_path=self._select_file_root_path,
                placeholder=FILE_NAME_PLACEHOLDER,
                validator_mode=self._default_validator_mode(),
            )
        yield from self.additional_content_after_input()
        yield DirectoryTreeHint("Or select from the directory tree:")
        yield DirectoryTree(str(self._select_file_root_path))

    def additional_content_after_input(self) -> ComposeResult:
        """
        Override this method to add additional content below the input.

        Returns:
            Additional content to be yielded.
        """
        return []

    @on(DirectoryTree.FileSelected)
    def _update_input_path(self, event: DirectoryTree.FileSelected) -> None:
        directory = event.path.parent
        self._file_name_input.update_root_directory_path(directory)
        self._update_relative_path_display(directory)
        self._file_name_input.input.value = event.path.name

    @on(DirectoryTree.DirectorySelected)
    def _update_input_path_from_directory(self, event: DirectoryTree.DirectorySelected) -> None:
        path = event.path
        self._file_name_input.update_root_directory_path(path)
        self._update_relative_path_display(path)

    def _update_relative_path_display(self, path: Path) -> None:
        self._path_display.path = humanize_relative_or_whole_path(
            path, self._select_file_root_path, add_trailing_slash=True
        )

    def _default_validator_mode(self) -> FilePathValidator.Modes:
        return "is_file"
