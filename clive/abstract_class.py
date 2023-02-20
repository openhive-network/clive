from __future__ import annotations

from abc import ABC, ABCMeta
from typing import Any

from textual.message_pump import MessagePumpMeta


class AbstractClass(ABC):
    """
    Abstract class that marks if some class cannot be instantiated.
    Even when no abstract methods were defined, this class cannot be instantiated. (default ABC allows for that)
    """

    def __new__(cls, abstract_type: type[AbstractClass] | None = None, *args, **kwargs) -> Any:  # type: ignore
        abstract_type = AbstractClass if abstract_type is None else abstract_type
        if abstract_type in cls.__bases__:
            raise TypeError(f"Abstract class `{cls.__name__}` cannot be instantiated.")

        if super().__new__ is object.__new__ and cls.__init__ is not object.__init__:
            return super().__new__(cls)
        return super().__new__(cls, *args, **kwargs)


class MessagePumpABCMeta(MessagePumpMeta, ABCMeta):
    """
    Combine MessagePumpMeta and ABCMeta into a single metaclass.
    Resolves the issue with:
        TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the
        metaclasses of all its bases
    """


class AbstractClassMessagePump(AbstractClass, metaclass=MessagePumpABCMeta):
    """
    Class used to mark all MessagePump derivatives (widget, screen, etc.) as Abstract.

    See the :class:`AbstractClass` class for more details.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        return super().__new__(cls, AbstractClassMessagePump, *args, **kwargs)
