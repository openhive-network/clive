from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Concatenate, ParamSpec

import typer

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
