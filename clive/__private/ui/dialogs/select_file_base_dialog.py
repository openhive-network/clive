from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import DirectoryTree, Label

from clive.__private.core.constants.tui.placeholders import PATH_PLACEHOLDER
from clive.__private.settings import safe_settings
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog, CliveActionDialogResultT
from clive.__private.ui.widgets.buttons.confirm_button import ConfirmOneLineButton
from clive.__private.ui.widgets.inputs.path_input import PathInput
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.validators.path_validator import PathValidator


class FilePathInputContainer(Horizontal):
    """Container for file path input and label."""


class DirectoryTreeHint(Label):
    """Hint for DirectoryTree widget."""


class SelectFileBaseDialog(CliveActionDialog[CliveActionDialogResultT], ABC):
    DEFAULT_CSS = """
    SelectFileBaseDialog {
        CliveDialogContent {
            width: 70%;
            height: 90%;

            FilePathInputContainer {
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
    def _file_path_input(self) -> PathInput:
        return self.query_exactly_one(PathInput)

    def create_dialog_content(self) -> ComposeResult:
        if self._notice:
            yield Notice(self._notice)
        with FilePathInputContainer():
            yield PathInput(placeholder=PATH_PLACEHOLDER, validator_mode=self._default_validator_mode())
        yield from self.additional_content_after_input()
        yield DirectoryTreeHint("Or select from the directory tree:")
        yield DirectoryTree(str(safe_settings.select_file_root_path))

    def additional_content_after_input(self) -> ComposeResult:
        """
        Override this method to add additional content below the input.

        Returns:
            Additional content to be yielded.
        """
        return []

    @on(DirectoryTree.FileSelected)
    @on(DirectoryTree.DirectorySelected)
    def _update_input_path(self, event: DirectoryTree.FileSelected) -> None:
        self._file_path_input.input.value = str(event.path)

    def _default_validator_mode(self) -> PathValidator.Modes:
        return "is_file"
