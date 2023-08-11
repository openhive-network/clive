from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import PERMLINK_PLACEHOLDER

if TYPE_CHECKING:
    from textual.widget import Widget


class PermlinkInput(TextInput):
    def __init__(
        self,
        to_mount: Widget,
        label: str = "permlink",
        value: str | None = None,
        placeholder: str = PERMLINK_PLACEHOLDER,
    ) -> None:
        super().__init__(to_mount=to_mount, label=label, value=value, placeholder=placeholder)
