from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from clive.__private.abstract_class import AbstractClassMessagePump

ContextT = TypeVar("ContextT")


class Contextual(Generic[ContextT], AbstractClassMessagePump):
    """A class that could return its context"""

    @property
    @abstractmethod
    def context(self) -> ContextT:
        """Return reference to context"""


class ContextualHolder(Contextual[ContextT]):
    """A class that holds a context"""

    def __init__(self, context: ContextT) -> None:
        self.__context = context
        super().__init__()

    @property
    def context(self) -> ContextT:
        return self.__context
