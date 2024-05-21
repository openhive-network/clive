from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from textual.binding import ActiveBinding

    ActiveBindingsMap: TypeAlias = dict[str, ActiveBinding]
