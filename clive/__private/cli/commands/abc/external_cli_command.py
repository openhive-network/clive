from __future__ import annotations

import errno
import inspect
from abc import ABC, abstractmethod
from dataclasses import Field, dataclass, field, fields
from typing import TYPE_CHECKING, Any, Self

from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.accounts.exceptions import NoWorkingAccountError
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile


@dataclass(kw_only=True)
class ExternalCLICommand(ABC):
    _skip_validation: bool = field(default=False, init=False)

    @abstractmethod
    async def _run(self) -> None:
        """Actual implementation of the command."""

    async def run(self) -> None:
        if not self._skip_validation:
            await self.validate()
        await self._configure()
        await self._run()

    async def validate(self) -> None:
        """
        Validate the command before running.

        If the command is invalid, raise an CLIPrettyError (or it's derivative) exception.
        """
        return

    async def _configure(self) -> None:
        """Configure the command before running."""
        return

    @classmethod
    def from_(cls, **kwargs: Any) -> Self:
        """
        Create an instance of a command from the given kwargs.

        Unused kwargs are ignored.

        Args:
            **kwargs: The kwargs to create the instance from.
        """
        sanitized = {k: v for k, v in kwargs.items() if k in inspect.signature(cls).parameters}
        return cls(**sanitized)

    def __get_initialized_fields(self) -> list[Field[Any]]:
        return [field_instance for field_instance in fields(self) if field_instance.init]

    def _supply_with_correct_default_for_working_account(self, profile: Profile) -> None:
        """
        We can load default working account value only during runtime.

        Profile name must be known when loading working account as working account is part of profile.
        """

        def get_working_account_name() -> str:
            try:
                return profile.accounts.working.name
            except NoWorkingAccountError as err:
                raise CLIPrettyError(
                    "Working account is not set, can't use working account as default.",
                    errno.EINVAL,
                ) from err

        for field_instance in self.__get_initialized_fields():
            field_name = field_instance.name
            field_value = getattr(self, field_name)
            if field_value == PERFORM_WORKING_ACCOUNT_LOAD:
                setattr(self, field_name, get_working_account_name())
            elif isinstance(field_value, list) and PERFORM_WORKING_ACCOUNT_LOAD in field_value:
                new_attr = [
                    get_working_account_name() if elem == PERFORM_WORKING_ACCOUNT_LOAD else elem for elem in field_value
                ]
                setattr(self, field_name, new_attr)
