from abc import ABC
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class PreconfiguredBaseModel(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed: bool = True

    @staticmethod
    def decorator(func: Callable[..., None]) -> Any:
        """Should be overridden in subclasses."""
