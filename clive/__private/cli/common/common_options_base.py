from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Concatenate, ParamSpec

import typer

from clive.models.base import CliveBaseModel

DecoratorParams = ParamSpec("DecoratorParams")

PreWrapFunc = Callable[Concatenate[typer.Context, DecoratorParams], Awaitable[None]]
PostWrapFunc = Callable[Concatenate[typer.Context, DecoratorParams], None]


class CommonOptionsBase(CliveBaseModel, ABC):
    """
    Common options for some commands.

    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597.
    """

    class Config:
        arbitrary_types_allowed: bool = True

    @classmethod
    @abstractmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        """Should be overridden in subclasses."""
