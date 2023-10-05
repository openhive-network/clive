from __future__ import annotations

from textual.binding import Binding

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen


class OperationBaseScreen(CartBasedScreen, AbstractClassMessagePump):
    """Base class for all screens that represent operations."""

    BINDINGS = [Binding("escape", "pop_screen", "Back")]
