from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar

from textual.containers import Grid

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class OperationSummary(OperationBaseScreen, OperationActionBindings, AbstractClassMessagePump):
    """Base class for operation summary screens."""

    CSS_PATH = [get_relative_css_path(__file__)]

    POP_SCREEN_AFTER_ADDING_TO_CART = True

    SECTION_TITLE: ClassVar[str] = "Operation summary"

    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES = False

    def create_left_panel(self) -> ComposeResult:
        with SectionScrollable(self.SECTION_TITLE, focusable=True), Body():
            yield from self.content()

    @abstractmethod
    def content(self) -> ComposeResult:
        """Create the content of the screen."""
