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

    In toml file this is represented as a key-value pair, i.e.:
    `lock_wallet = "ctrl+l"` means the id is `lock_wallet` and the key is `ctrl+l`.

    Attributes:
        id: Unique identifier for the binding
        key: Keyboard shortcut (e.g., "ctrl+x")
        description: Human-readable description of the binding action
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
        """Handles the general logic how binding should be displayed in the TUI."""
        return self._key_short

    @property
    def button_display(self) -> str:
        """Handles the logic how binding should be displayed in the Button widgets."""
        return self.bindings_display

    @property
    def _key_short(self) -> str:
        """Returns a shortened version of the key binding (replacing 'ctrl+' with '^')."""
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
        """Creates a Textual binding object from this instance.

        Args:
            action: The action to perform (defaults to binding id if empty)
            description: The binding description (defaults to a humanized version of binding id if empty)
            show: Whether to show the binding in the footer
            key_display: Custom display for the key binding in the footer
            priority: Whether this binding has priority
            tooltip: Tooltip text for the binding

        Returns:
            A Textual binding object configured with this binding's or explicitly overridden properties
        """
        action_ = action if action is not None else self.id
        description_ = description or self.description or ""
        return Binding(self.key, action_, description_, show, key_display, priority, tooltip, self.id)
