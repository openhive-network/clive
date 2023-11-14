from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any, Concatenate, ParamSpec

import typer
from typing_extensions import Self

from clive.core.url import Url
from clive.models.base import CliveBaseModel

DecoratorParams = ParamSpec("DecoratorParams")

PreWrapFunc = Callable[Concatenate[typer.Context, DecoratorParams], Awaitable[None]]
PostWrapFunc = Callable[Concatenate[typer.Context, DecoratorParams], None]


class CommonBaseModel(CliveBaseModel, ABC):
    class Config:
        arbitrary_types_allowed: bool = True

    @classmethod
    @abstractmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        """Should be overridden in subclasses."""

    @classmethod
    def validate_options(cls, data: dict[str, Any]) -> None:
        """
        Should perform all options validations.

        Because typer does not implement mutually exclusive options or options groups, we need to validate them manually.
        e.g. if `sign` is passed, `password` must be passed too.

        If validation fails, CLIPrettyError (or its derivatives) should be raised.

        Args:
        ----
        data: The data to validate. Should be a dict of the options passed to the command.
        """

        def construct() -> Self:  # type: ignore[type-var, misc]
            nonlocal data
            data = {k: v for k, v in data.items() if k in cls.__fields__}  # sanitize
            return cls(**data)  # type: ignore[return-value]

        obj: Self = construct()
        obj._validate_options()

    @staticmethod
    def update_forwards() -> None:
        """All forwards references will be imported here."""

    def _validate_options(self) -> None:
        """Put all options validations here. See: `validate_options`."""

    @staticmethod
    def _print_launching_beekeeper(
        beekeeper_remote_endpoint: Url | None,
        condition: bool = True,
    ) -> None:
        if condition:
            typer.echo(
                "Launching beekeeper..."
                if not beekeeper_remote_endpoint
                else f"Using beekeeper at {beekeeper_remote_endpoint}"
            )

    @staticmethod
    def _assert_correct_profile_is_loaded(loaded_name: str, expected_name: str) -> None:
        assert loaded_name == expected_name, f"Wrong profile loaded. Got `{loaded_name}` but expected `{expected_name}`"
