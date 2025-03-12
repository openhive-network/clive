from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias

if TYPE_CHECKING:
    from textual.binding import ActiveBinding

    ActiveBindingsMap: TypeAlias = dict[str, ActiveBinding]

CliveModes = Literal["unlock", "create_profile", "dashboard", "config", "_default"]
"""Modes that Clive can run in. The `_default` mode is the first mode that is set by Textual when Clive starts."""
