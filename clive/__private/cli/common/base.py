from abc import ABC
from collections.abc import Callable
from typing import Any

import typer
from pydantic import BaseModel

from clive.core.url import Url


class PreconfiguredBaseModel(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed: bool = True

    @classmethod
    def decorator(cls, func: Callable[..., Any]) -> Any:
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
