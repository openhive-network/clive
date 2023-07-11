import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from typing_extensions import Self


@dataclass(kw_only=True)
class ExternalCLICommand(ABC):
    @abstractmethod
    def run(self) -> None:
        """Run the command."""

    @classmethod
    def from_(cls, **kwargs: Any) -> Self:
        """
        Create an instance of a command from the given kwargs.

        Unused kwargs are ignored.

        Args:
        ----
        **kwargs: The kwargs to create the instance from.
        """
        sanitized = {k: v for k, v in kwargs.items() if k in inspect.signature(cls).parameters}
        return cls(**sanitized)
