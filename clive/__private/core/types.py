from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MigrationStatus = Literal["migrated", "already_newest"]
NotifyLevel = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class BindingIdKey:
    """Unique id of the binding and corresponding key from keyboard or key combination."""

    id: str
    key: str
