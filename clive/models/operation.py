from __future__ import annotations

import dataclasses
from abc import abstractmethod
from itertools import count
from typing import Any, ClassVar

from clive.abstract_class import AbstractClass


@dataclasses.dataclass
class Operation(AbstractClass):
    __instance_count: ClassVar[count[int]] = count(0)

    type_: str

    # this field is just to grant uniqueness of each operation
    _id: int = dataclasses.field(
        default_factory=lambda: next(Operation.__instance_count),
        init=False,
        hash=True,
        repr=False,
        compare=True,
    )

    def as_json(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @abstractmethod
    def pretty_print(self) -> str:
        """This method should return short, formatted description of operation without op type"""

    @abstractmethod
    def is_valid(self) -> bool:
        """This is abstract method, that should be implemented by each child"""
