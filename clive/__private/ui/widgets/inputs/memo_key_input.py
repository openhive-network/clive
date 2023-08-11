from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.placeholders_constants import KEY_PLACEHOLDER

if TYPE_CHECKING:
    from textual.widget import Widget


class MemoKeyInput(TextInput):
    def __init__(
        self, to_mount: Widget, label: str = "memo key", placeholder: str = KEY_PLACEHOLDER, value: str | None = None
    ):
        super().__init__(to_mount=to_mount, label=label, placeholder=placeholder, value=value)
