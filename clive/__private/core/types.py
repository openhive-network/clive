from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

NotifyLevel = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class BindingIdKey:
    """Unique id of the binding and corresponding key or key combination from keyboard."""

    id: str
    key: str
