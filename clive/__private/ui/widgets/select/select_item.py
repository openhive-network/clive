from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SelectItemType = Any


@dataclass
class SelectItem:
    value: SelectItemType
    text: str
