from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.profile_data import ProfileData, ProfileInvalidNameError
from clive.__private.ui.widgets.clive_highlighter import CliveHighlighter
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import PROFILE_NAME_PLACEHOLDER

if TYPE_CHECKING:
    from rich.console import RenderableType


class ProfileNameHighlighter(CliveHighlighter):
    def is_valid_value(self, value: str) -> bool:
        try:
            ProfileData.validate_profile_name(value)
        except ProfileInvalidNameError:
            return False
        return True


class ProfileNameInput(TextInput):
    def __init__(
        self,
        label: str = "profile name",
        value: str | None = None,
        *,
        placeholder: str = PROFILE_NAME_PLACEHOLDER,
        tooltip: RenderableType | None = None,
        disabled: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            label=label,
            value=value,
            placeholder=placeholder,
            tooltip=tooltip,
            disabled=disabled,
            highlighter=ProfileNameHighlighter(),
            id_=id_,
            classes=classes,
        )

    @property
    def value(self) -> str | None:  # type: ignore[override]
        value = self._input.value
        highlighter: ProfileNameHighlighter = self._highlighter  # type: ignore[assignment]

        if not highlighter.is_valid_value(value):
            self.notify("Invalid profile name", severity="error")
            return None
        return value
