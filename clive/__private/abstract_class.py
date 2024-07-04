from __future__ import annotations

from abc import ABC, ABCMeta

from textual.message_pump import _MessagePumpMeta


class MessagePumpABCMeta(_MessagePumpMeta, ABCMeta):
    """
    Combine MessagePumpMeta and ABCMeta into a single metaclass.

    Resolves the issue with:
        TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the
        metaclasses of all its bases.
    """


class AbstractClassMessagePump(ABC, metaclass=MessagePumpABCMeta):
    """Class used to mark all MessagePump derivatives (widget, screen, etc.) abstract as regular ABC doesn't work."""
