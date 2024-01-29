from __future__ import annotations

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.bindings import OperationActionBindings
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen


class RawOperationBaseScreen(OperationBaseScreen, OperationActionBindings, AbstractClassMessagePump):
    """Base class for all raw operations."""
