from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.clive_import import get_clive
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
        return self._key_display

    @property
    def button_display(self) -> str:
        """Handles the logic how binding should be displayed in the Button widgets."""
        return self.bindings_display

    @property
    def default_action(self) -> str:
        return self.id

    @property
    def _key_display(self) -> str:
        """Handles the logic how to display the binding key."""
        key = self.key.split(",")[0]  # display only first key if there are multiple defined
        app = get_clive().app_instance()
        return app.get_key_display(Binding(key, ""))

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
        action_ = action if action is not None else self.default_action
        description_ = description or self.description or ""
        return Binding(self.key, action_, description_, show, key_display, priority, tooltip, self.id)
