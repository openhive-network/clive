from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from clive.__private.abstract_class import AbstractClassMessagePump

if TYPE_CHECKING:
    from typing_extensions import Self


class Context:
    """A class that could be used as a context."""

    def update_from_context(self, context: Self) -> None:
        """Updates self from other context."""
        for attribute in self.__dict__:
            setattr(self, attribute, getattr(context, attribute))


ContextT = TypeVar("ContextT", bound=Context | None)


class Contextual(Generic[ContextT], AbstractClassMessagePump):
    """A class that could return its context."""

    @property
    @abstractmethod
    def context(self) -> ContextT:
        """Return reference to context."""


class ContextualHolder(Contextual[ContextT]):
    """A class that holds a context."""

    def __init__(self, context: ContextT) -> None:
        self.__context = context
        super().__init__()

    @property
    def context(self) -> ContextT:
        return self.__context
