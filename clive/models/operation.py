from __future__ import annotations

import json
from abc import abstractmethod

from pydantic import BaseModel

from clive.__private.abstract_class import AbstractClass


class Operation(BaseModel, AbstractClass):
    def as_json(self, indent: int = 4) -> str:
        return json.dumps(self.dict(by_alias=True), indent=indent)

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the operation."""

    @abstractmethod
    def pretty(self, *, separator: str = "\n") -> str:
        """This method should return short, formatted description of operation without op type"""
