from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Container
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Button, Static

from clive.__private.ui.operations.tranaction_summary import TransactionSummary
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from typing_extensions import Self

    from clive.__private.core.profile_data import ProfileData
    from clive.models.operation import Operation


class DynamicColumn(DynamicLabel):
    """Column with dynamic content"""


class StaticColumn(Static):
    """Column with static content"""


class ColumnLayout(Static):
    """This class holds column order"""


class ButtonMoveUp(Button):
    """Button used for moving the operation up in the cart"""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("🔼", id="move-up-button", disabled=disabled)


class ButtonMoveDown(Button):
    """Button used for moving the operation down in the cart"""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("🔽", id="move-down-button", disabled=disabled)


class ButtonDelete(Button):
    """Button used for removing the operation from cart"""

    def __init__(self) -> None:
        super().__init__("🗑️", id="delete-button")


class StaticPart(Static):
    """Container for the static part of the screen - title, global buttons and table header"""


class ScrollablePart(Container):
    """Container used for holding operation items"""


class DetailedCartOperation(ColumnLayout, CliveWidget):
    BINDINGS = [
        Binding("ctrl+up", "select_previous", "Prev"),
        Binding("ctrl+down", "select_next", "Next"),
    ]

    class Deleted(Message):
        def __init__(self, deleted: Operation) -> None:
            self.deleted = deleted
            super().__init__()

    class Move(Message):
        def __init__(self, from_idx: int, to_idx: int) -> None:
            self.from_idx = from_idx
            self.to_idx = to_idx
            super().__init__()

    class Focus(Message):
        """Message sent when other DetailedCartOperation should be focused"""

        def __init__(self, target_idx: int) -> None:
            self.target_idx = target_idx
            super().__init__()

    def __init__(self, operation_idx: int) -> None:
        self.__idx = operation_idx
        assert self.is_valid(), "During construction, index has to be valid"
        super().__init__()

    def __repr__(self) -> str:
        return f"DetailedCartOperation({self.__idx=})"

    def on_mount(self) -> None:
        if self.__is_first:
            self.unbind("ctrl+up")
        elif self.__is_last:
            self.unbind("ctrl+down")

    def is_valid(self) -> bool:
        return self.__idx < self.__operations_count

    def compose(self) -> ComposeResult:
        def operation_index(_: ProfileData) -> str:
            if self.is_valid():
                return f"{self.__idx + 1}."
            return ""

        def operation_name(_: ProfileData) -> str:
            if self.is_valid():
                return self.__operation.get_name()
            return ""

        def operation_details(_: ProfileData) -> str:
            if self.is_valid():
                return self.__operation.pretty()
            return ""

        yield DynamicColumn(
            self.app, "profile_data", operation_index, id_="operation_position_in_trx", classes="cell cell-middle"
        )
        yield DynamicColumn(
            self.app, "profile_data", operation_name, id_="operation_type", classes="cell cell-variant cell-middle"
        )
        yield DynamicColumn(self.app, "profile_data", operation_details, id_="operation_details", classes="cell")
        yield ButtonMoveUp(disabled=self.__is_first)
        yield ButtonMoveDown(disabled=self.__is_last)
        yield ButtonDelete()

    def focus(self, _: bool = True) -> Self:
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
    def __operations_count(self) -> int:
        return len(self.app.profile_data.transaction)

    @property
    def __operation(self) -> Operation:
        assert self.is_valid(), "cannot get operation, position is invalid"
        return self.app.profile_data.transaction.get(self.__idx)

    @property
    def __is_first(self) -> bool:
        return self.__idx == 0

    @property
    def __is_last(self) -> bool:
        return self.__idx == self.__operations_count - 1

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "delete-button":
            self.post_message(self.Deleted(self.__operation))
        elif event.button.id == "move-up-button":
            self.post_message(self.Move(self.__idx, self.__idx - 1))
        elif event.button.id == "move-down-button":
            self.post_message(self.Move(self.__idx, self.__idx + 1))

    def on_detailed_cart_operation_move(self, event: DetailedCartOperation.Move) -> None:
        if event.to_idx == self.__idx:
            self.__idx = event.from_idx
        self.app.update_reactive("profile_data")


class CartOperationsHeader(ColumnLayout):
    def compose(self) -> ComposeResult:
        yield StaticColumn("No.", id="operation_position_in_trx", classes="cell cell-middle")
        yield StaticColumn("Operation Type", id="operation_type", classes="cell cell-variant cell-middle")
        yield StaticColumn("Operation Details", id="operation_details", classes="cell cell-middle")
        yield StaticColumn("Move Up", classes="cell cell-variant cell-middle")
        yield StaticColumn("Move Down", classes="cell cell-middle")
        yield StaticColumn("Delete", classes="cell cell-variant cell-middle")


class Cart(BaseScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f9", "clear_all", "Clear all"),
        Binding("f10", "summary", "Summary"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.__scrollable_part = ScrollablePart()

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            with StaticPart():
                yield BigTitle("operations cart")
                yield CartOperationsHeader()

            with self.__scrollable_part:
                for idx in range(len(self.app.profile_data.transaction)):
                    yield DetailedCartOperation(idx)

            yield Static()

    def on_detailed_cart_operation_deleted(self, event: DetailedCartOperation.Deleted) -> None:
        widget = self.query(DetailedCartOperation).last()
        self.app.profile_data.transaction.remove(event.deleted)
        widget.add_class("deleted")
        widget.remove()
        self.app.update_reactive("profile_data")

    def on_detailed_cart_operation_move(self, event: DetailedCartOperation.Move) -> None:
        assert event.to_idx >= 0 and event.to_idx < len(self.app.profile_data.transaction)

        self.app.profile_data.transaction.swap_order(event.from_idx, event.to_idx)
        self.app.update_reactive("profile_data")

    def on_detailed_cart_operation_focus(self, event: DetailedCartOperation.Focus) -> None:
        for detailed in self.query(DetailedCartOperation):
            if event.target_idx == detailed.idx:
                detailed.focus()

    def action_summary(self) -> None:
        self.app.push_screen(TransactionSummary())

    def action_clear_all(self) -> None:
        self.app.profile_data.transaction.clear()
        self.app.update_reactive("profile_data")
        self.__scrollable_part.add_class("-hidden")
