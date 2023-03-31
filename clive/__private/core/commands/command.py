from __future__ import annotations

from abc import abstractmethod
from typing import Any

from clive.__private.abstract_class import AbstractClass


class Command(AbstractClass):
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Executes the command"""
