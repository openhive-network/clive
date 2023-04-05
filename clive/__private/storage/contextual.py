from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from clive.__private.abstract_class import AbstractClassMessagePump

ContextT = TypeVar("ContextT")


class Contextual(Generic[ContextT], AbstractClassMessagePump):
    @abstractmethod
    def get_context(self) -> ContextT:
        """Return reference to context"""

    @property
    def context(self) -> ContextT:
        return self.get_context()


class ContextualHolder(Contextual[ContextT]):
    def __init__(self, context: ContextT) -> None:
        self.__context = context
        super().__init__()

    def get_context(self) -> ContextT:
        return self.__context
