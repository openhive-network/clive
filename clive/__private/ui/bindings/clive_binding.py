from __future__ import annotations

from dataclasses import dataclass

import inflection
from textual.binding import Binding


@dataclass
class CliveBinding:
    """Represents a single keyboard binding in the application that can be configured.

    Attributes:
        id: Unique identifier for the binding
        key: Keyboard shortcut (e.g., "ctrl+x")
        description: Human-readable description of the binding action
    """

    id: str
    key: str
    description: str | None = None

    def __post_init__(self) -> None:
        if self.description is None:
            self.description = inflection.humanize(self.id)

    @property
    def button_display(self) -> str:
        """Handles the logic how binding should be displayed in the Button widgets."""
        return self.key_short

    @property
    def key_short(self) -> str:
        """Returns a shortened version of the key binding (replacing 'ctrl+' with '^')."""
        return self.key.replace("ctrl+", "^")

    def create(
        self,
        *,
        action: str = "",
        description: str = "",
        show: bool = True,
        key_display: str | None = None,
        priority: bool = False,
        tooltip: str = "",
    ) -> Binding:
        """Creates a Textual Binding object from this CliveConfigurableBinding.

        Args:
            action: The action to perform (defaults to binding id if empty)
            description: The binding description (defaults to CliveConfigurableBinding description if empty)
            show: Whether to show the binding in the footer
            key_display: Custom display for the key binding in the footer
            priority: Whether this binding has priority
            tooltip: Tooltip text for the binding

        Returns:
            A Textual Binding object configured with this binding's properties
        """
        action_ = action or self.id
        description_ = description or self.description or ""
        return Binding(self.key, action_, description_, show, key_display, priority, tooltip, self.id)
