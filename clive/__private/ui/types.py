from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from textual.binding import ActiveBinding

    type ActiveBindingsMap = dict[str, ActiveBinding]

CliveModes = Literal["unlock", "create_profile", "dashboard", "settings", "_default"]
"""Modes that Clive can run in. The `_default` mode is the first mode that is set by Textual when Clive starts."""
