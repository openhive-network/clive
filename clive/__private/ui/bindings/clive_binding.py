from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.formatters.humanize import humanize_binding_id

if TYPE_CHECKING:
    from clive.__private.ui.bindings.types import BindingID, KeyboardShortcut


@dataclass
class CliveBinding:
    """
    This class maps a binding ID to a keyboard shortcut.

    In toml file this is reprezented as key-value pair, i.e.:
    `lock_wallet = "ctrl+l` where id is `lock_wallet` and key is `ctrl+l`.
    """

    id: BindingID
    key: KeyboardShortcut
    description: str | None = None
    """Will be determined from id if not given"""

    def __post_init__(self) -> None:
        if self.description is None:
            self.description = humanize_binding_id(self.id)

    @property
    def bindings_display(self) -> str:
        return self._key_short

    @property
    def button_display(self) -> str:
        return self.bindings_display

    @property
    def _key_short(self) -> str:
        return self.key.replace("ctrl+", "^")

    def create(
        self,
        *,
        action: str | None = None,
        description: str = "",
        show: bool = True,
        key_display: str | None = None,
        priority: bool = False,
        tooltip: str = "",
    ) -> Binding:
        action_ = action if action is not None else self.id
        description_ = description or self.description or ""
        return Binding(self.key, action_, description_, show, key_display, priority, tooltip, self.id)
