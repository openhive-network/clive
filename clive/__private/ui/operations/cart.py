from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Container
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_operation_details, humanize_operation_name
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.transaction_summary import TransactionSummaryFromCart
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from typing_extensions import Self

    from clive.__private.core.profile import Profile
    from clive.__private.models.schemas import OperationBase


class DynamicColumn(DynamicLabel):
    """Column with dynamic content."""


class StaticColumn(Static):
    """Column with static content."""


class ColumnLayout(Static):
    """Holds column order."""


class ButtonMoveUp(CliveButton):
    """Button used for moving the operation up in the cart."""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↑", id_="move-up-button", disabled=disabled)


class ButtonMoveDown(CliveButton):
    """Button used for moving the operation down in the cart."""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↓", id_="move-down-button", disabled=disabled)


class ButtonDelete(CliveButton):
    """Button used for removing the operation from cart."""

    def __init__(self) -> None:
        super().__init__("Remove", id_="delete-button")


class StaticPart(Container):
    """Container for the static part of the screen - title, global buttons and table header."""


class CartItem(ColumnLayout, CliveWidget):
    BINDINGS = [
        Binding("ctrl+up", "select_previous", "Prev"),
        Binding("ctrl+down", "select_next", "Next"),
    ]

    class Delete(Message):
        def __init__(self, widget: CartItem) -> None:
            self.widget = widget
            super().__init__()

    class Move(Message):
        def __init__(self, from_idx: int, to_idx: int) -> None:
            self.from_idx = from_idx
            self.to_idx = to_idx
            super().__init__()

    class Focus(Message):
        """Message sent when other CartItem should be focused."""

        def __init__(self, target_idx: int) -> None:
            self.target_idx = target_idx
            super().__init__()

    def __init__(self, operation_idx: int) -> None:
        self.__idx = operation_idx
        assert self.is_valid(), "During construction, index has to be valid"
        super().__init__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(idx={self.__idx})"

    def on_mount(self) -> None:
        if self.__is_first:
            self.unbind("ctrl+up")
        elif self.__is_last:
            self.unbind("ctrl+down")

    def is_valid(self) -> bool:
        return self.__idx < self.__operations_count

    def compose(self) -> ComposeResult:
        def get_operation_index(_: Profile) -> str:
            return f"{self.__idx + 1}." if self.is_valid() else "?"

        def get_operation_name(_: Profile) -> str:
            return humanize_operation_name(self.operation) if self.is_valid() else "?"

        def get_operation_details(_: Profile) -> str:
            return humanize_operation_details(self.operation) if self.is_valid() else "?"

        yield DynamicColumn(
            self.world,
            "profile",
            get_operation_index,
            classes="cell cell-middle",
        )
        yield DynamicColumn(
            self.world,
            "profile",
            get_operation_name,
            shrink=True,
            classes="cell cell-variant cell-middle",
        )
        yield DynamicColumn(
            self.world,
            "profile",
            get_operation_details,
            shrink=True,
            classes="cell",
        )
        yield ButtonMoveUp(disabled=self.__is_first)
        yield ButtonMoveDown(disabled=self.__is_last)
        yield ButtonDelete()

    def focus(self, _: bool = True) -> Self:  # noqa: FBT001, FBT002
        if focused := self.app.focused:  # Focus the corresponding button as it was before
            assert focused.id, "Previously focused widget has no id!"
            with contextlib.suppress(NoMatches):
                previous = self.get_child_by_id(focused.id)
                if previous.focusable:
                    previous.focus()
                    return self

        for child in reversed(self.children):  # Focus first focusable
            if child.focusable:
                child.focus()

        return self

    def action_select_previous(self) -> None:
        self.post_message(self.Focus(target_idx=self.__idx - 1))

    def action_select_next(self) -> None:
        self.post_message(self.Focus(target_idx=self.__idx + 1))

    @property
    def idx(self) -> int:
        return self.__idx

    @property
    def operation(self) -> OperationBase:
        assert self.is_valid(), "cannot get operation, position is invalid"
        return self.profile.cart[self.__idx]

    @property
    def __operations_count(self) -> int:
        return len(self.profile.cart)

    @property
    def __is_first(self) -> bool:
        return self.__idx == 0

    @property
    def __is_last(self) -> bool:
        return self.__idx == self.__operations_count - 1

    @on(CliveButton.Pressed, "#move-up-button")
    def move_up(self) -> None:
        self.post_message(self.Move(from_idx=self.__idx, to_idx=self.__idx - 1))

    @on(CliveButton.Pressed, "#move-down-button")
    def move_down(self) -> None:
        self.post_message(self.Move(from_idx=self.__idx, to_idx=self.__idx + 1))

    @on(CliveButton.Pressed, "#delete-button")
    def delete(self) -> None:
        self.post_message(self.Delete(self))

    @on(Move)
    def move_item(self, event: CartItem.Move) -> None:
        if event.to_idx == self.__idx:
            self.__idx = event.from_idx
        self.app.trigger_profile_watchers()


class CartHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", classes="cell cell-middle")
        yield StaticColumn("Operation type", classes="cell cell-variant cell-middle")
        yield StaticColumn("Operation details", classes="cell cell-middle")
        yield StaticColumn("Actions", id="actions", classes="cell cell-variant cell-middle")


class Cart(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f9", "clear_all", "Clear all"),
        Binding("f6", "summary", "Summary"),
    ]
    BIG_TITLE = "operations cart"

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        with StaticPart():
            yield CartHeader()

        with self.__scrollable_part:
            yield from self.__rebuild_items()

    def __rebuild_items(self) -> ComposeResult:
        for idx in range(len(self.profile.cart)):
            yield CartItem(idx)

    @on(CartItem.Delete)
    def remove_item(self, event: CartItem.Delete) -> None:
        self.profile.cart.remove(event.widget.operation)
        self.app.trigger_profile_watchers()
        self.__scrollable_part.query(CartItem).remove()
        self.__scrollable_part.mount(*self.__rebuild_items())

    @on(CartItem.Move)
    def move_item(self, event: CartItem.Move) -> None:
        assert event.to_idx >= 0
        assert event.to_idx < len(self.profile.cart)

        self.profile.cart.swap(event.from_idx, event.to_idx)
        self.app.trigger_profile_watchers()

    @on(CartItem.Focus)
    def focus_item(self, event: CartItem.Focus) -> None:
        for cart_item in self.query(CartItem):
            if event.target_idx == cart_item.idx:
                cart_item.focus()

    def action_summary(self) -> None:
        self.app.push_screen(TransactionSummaryFromCart())

    def action_clear_all(self) -> None:
        self.profile.cart.clear()
        self.app.trigger_profile_watchers()
        self.__scrollable_part.add_class("-hidden")
