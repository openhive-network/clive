from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

SelectItemValueType = TypeVar("SelectItemValueType")


@dataclass
class SelectItem(Generic[SelectItemValueType]):
    value: SelectItemValueType
    text: str
