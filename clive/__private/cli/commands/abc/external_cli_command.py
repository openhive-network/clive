import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from typing_extensions import Self


@dataclass(kw_only=True)
class ExternalCLICommand(ABC):
    _skip_validation: bool = field(default=False, init=False)

    @abstractmethod
    async def _run(self) -> None:
        """The actual implementation of the command."""

    async def run(self) -> None:
        if not self._skip_validation:
            await self.validate()
        await self._run()

    async def validate(self) -> None:
        """
        Validate the command.

        If the command is invalid, raise an CLIPrettyError (or it's derivative) exception.

        Raises
        ------
        CLIPrettyError: If the command is invalid.
        """
        return

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
