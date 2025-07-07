from __future__ import annotations

from typing import Generic, Literal, overload

from typing_extensions import TypeVar

from clive.__private.cli.completion import is_tab_completion_active

if not is_tab_completion_active():
    from clive.__private.cli.exceptions import CLIPrettyError


ExpectedT = TypeVar("ExpectedT", default=str)


class EnsureSingleValue(Generic[ExpectedT]):
    def __init__(self, option_name: str) -> None:
        self._option_name = option_name

    @overload
    def of(
        self,
        positional: ExpectedT | None,
        option: ExpectedT | None,
        *,
        allow_none: Literal[False] = False,
    ) -> ExpectedT: ...

    @overload
    def of(
        self,
        positional: ExpectedT | None,
        option: ExpectedT | None,
        *,
        allow_none: Literal[True],
    ) -> ExpectedT | None: ...

    def of(
        self,
        positional: ExpectedT | None,
        option: ExpectedT | None,
        *,
        allow_none: bool = False,
    ) -> ExpectedT | None:
        """
        Ensure that only one value is retrieved.

        Option takes precedence over positional argument

        Args:
            positional: The positional argument value.
            option: The option argument value.
            allow_none: When argument and option is not required.
        """
        if allow_none and positional is None and option is None:
            return None

        value = option if option is not None else positional
        if value is None:
            raise CLIPrettyError(
                f"Missing required argument or option: '[{self._option_name.upper()}]' or '--{self._option_name}'."
            )
        return value


class EnsureSingleAccountNameValue(EnsureSingleValue[str]):
    def __init__(self) -> None:
        super().__init__("account-name")


class EnsureSingleProfileNameValue(EnsureSingleValue[str]):
    def __init__(self) -> None:
        super().__init__("profile-name")
