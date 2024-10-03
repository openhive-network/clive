from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import DOMQuery, NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, Select, Static
from typing_extensions import Self

from clive.__private.core.commands.abc.command_in_unlocked import CommandRequiresUnlockedModeError
from clive.__private.core.commands.load_transaction import LoadTransactionError
from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.core.formatters import humanize
from clive.__private.core.formatters.humanize import humanize_operation_details, humanize_operation_name
from clive.__private.core.keys import PublicKey
from clive.__private.core.keys.key_manager import KeyNotFoundError
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs.raw_json_dialog import RawJsonDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.buttons.remove_button import ButtonRemove
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select_file import SelectFile
from clive.__private.ui.widgets.select_file_to_save_transaction import SelectFileToSaveTransaction

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widgets._select import NoSelection

    from clive.__private.models import Transaction
    from clive.__private.models.schemas import OperationBase


class TransactionExpirationLabel(Label):
    """Label for displaying transaction expiration."""


class TransactionIdLabel(Label):
    """Label for displaying transaction id."""


class TransactionMetadataContainer(Horizontal):
    """Container for the transaction metadata."""

    transaction: Transaction | None = reactive(None, init=False, recompose=True)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction | None):
        super().__init__()
        self.transaction = transaction

    def compose(self) -> ComposeResult:
        if self.transaction:
            expiration = humanize.humanize_datetime(self.transaction.expiration)
            yield TaposHolder(self.transaction)
            yield TransactionExpirationLabel(f"Expiration: {expiration}")
            yield TransactionIdLabel(f"Transaction ID: {self.transaction.calculate_transaction_id()}")
        else:
            yield Label("No operations in cart, can't calculate transaction metadata.", id="no-metadata")

    def watch_transaction(self, _: Transaction | None) -> None:
        if self.transaction:
            self.query(TaposHolder).transaction = self.transaction


class ButtonMoveUp(CliveButton):
    """Button used for moving the operation up in the cart."""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↑", id_="move-up-button", disabled=disabled)


class ButtonMoveDown(CliveButton):
    """Button used for moving the operation down in the cart."""

    def __init__(self, *, disabled: bool = False) -> None:
        super().__init__("↓", id_="move-down-button", disabled=disabled)


class ButtonBroadcast(CliveButton):
    """Button used to broadcasting transaction."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that broadcast button was pressed."""

    def __init__(self) -> None:
        super().__init__("Broadcast (F6)", variant="success")


class ButtonSave(CliveButton):
    """Button used to save transaction to file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that save button was pressed."""

    def __init__(self) -> None:
        super().__init__("Save to file (F2)")


class ButtonOpenTransactionFromFile(CliveButton):
    """Button used to load transaction from file."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that open from file button was pressed."""

    def __init__(self) -> None:
        super().__init__("Open from file (F3)")


class ButtonRawJson(CliveButton):
    """Button used for displaying raw json of single operation added to cart."""

    class Pressed(CliveButton.Pressed):
        """Used to identify exactly that raw json button was pressed."""

    def __init__(self) -> None:
        super().__init__("JSON", id_="raw-json-button")


class TaposHolder(Vertical):
    """Container for the TaPoS metadata."""

    transaction: Transaction | None = reactive(None, init=False)  # type: ignore[assignment]

    def __init__(self, transaction: Transaction | None) -> None:
        super().__init__()
        self._ref_block_num_label = Label(f"Ref block num: {self.transaction.ref_block_num}", id="ref-block-num")
        self._ref_block_prefix_label = Label(
            f"Ref block prefix: {self.transaction.ref_block_prefix}", id="ref-block-prefix"
        )

    def compose(self) -> ComposeResult:
        yield Label("TaPoS:")
        yield self._ref_block_num_label
        yield self._ref_block_prefix_label

    def watch_transaction(self, _: Transaction) -> None:
        if self.transaction:
            self._ref_block_num_label.update(f"Ref block num: {self.transaction.ref_block_num}")
            self._ref_block_prefix_label.update(f"Ref block prefix: {self.transaction.ref_block_prefix}")


class SelectKey(SafeSelect[PublicKey], CliveWidget):
    """Combobox for selecting the public key."""

    def __init__(self) -> None:
        try:
            first_value: PublicKey | NoSelection = self.profile.keys.first
        except KeyNotFoundError:
            first_value = Select.BLANK

        super().__init__(
            [(key.alias, key) for key in self.profile.keys],
            value=first_value,
            empty_string="no private key found",
        )


class KeyHint(Label):
    """Hint for the key."""


@dataclass
class CartItemsActionManager:
    """Object used for disabling actions like move/delete on cart items while another action is in progress."""

    _is_action_disabled: bool = False

    @property
    def is_action_disabled(self) -> bool:
        return self._is_action_disabled

    def enable_action(self) -> None:
        self._is_action_disabled = False

    def disable_action(self) -> None:
        self._is_action_disabled = True


class CartItem(CliveCheckerboardTableRow, CliveWidget):
    """Row of CartTable."""

    BINDINGS = [
        Binding("ctrl+up", "select_previous", "Prev"),
        Binding("ctrl+down", "select_next", "Next"),
    ]

    operation_index: int = reactive(0, init=False)  # type: ignore[assignment]

    @dataclass
    class Delete(Message):
        widget: CartItem

    @dataclass
    class Move(Message):
        from_index: int
        to_index: int

    @dataclass
    class Focus(Message):
        """Message sent when other CartItem should be focused."""

        target_index: int

    def __init__(self, operation_index: int, action_manager: CartItemsActionManager) -> None:
        assert self._is_operation_index_valid(operation_index), "During construction, operation index has to be valid"
        self._operation_index = operation_index
        super().__init__(*self._create_cells())
        self._action_manager = action_manager

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operation_index={self._operation_index})"

    @property
    def operation_number_cell(self) -> CliveCheckerBoardTableCell:
        return self.query(CliveCheckerBoardTableCell).first()

    @property
    def button_move_up(self) -> ButtonMoveUp:
        return self.query_one(ButtonMoveUp)

    @property
    def button_move_down(self) -> ButtonMoveDown:
        return self.query_one(ButtonMoveDown)

    @property
    def button_delete(self) -> ButtonRemove:
        return self.query_one(ButtonRemove)

    @property
    def operation(self) -> OperationBase:
        assert self._is_operation_index_valid(self._operation_index), "Cannot get operation, position is invalid."
        return self.profile.cart[self._operation_index]

    @property
    def operations_amount(self) -> int:
        return len(self.profile.cart)

    @property
    def is_first(self) -> bool:
        return self._operation_index == 0

    @property
    def is_last(self) -> bool:
        return self._operation_index == self.operations_amount - 1

    def on_mount(self) -> None:
        self.operation_index = self._operation_index

        if self.is_first:
            self.unbind("ctrl+up")
        elif self.is_last:
            self.unbind("ctrl+down")

    def watch_operation_index(self, value: int) -> None:
        assert self._is_operation_index_valid(value), "Operation index is invalid when trying to update."
        self._operation_index = value
        self.operation_number_cell.update_content(self.humanize_operation_number())

    def humanize_operation_number(self, *, before_removal: bool = False) -> str:
        cart_items = len(self.profile.cart) - 1 if before_removal else len(self.profile.cart)
        return f"{self._operation_index + 1}/{cart_items}"

    def humanize_operation_name(self) -> str:
        return humanize_operation_name(self.operation)

    def humanize_operation_details(self) -> str:
        return humanize_operation_details(self.operation)

    def action_select_previous(self) -> None:
        self.post_message(self.Focus(target_index=self._operation_index - 1))

    def action_select_next(self) -> None:
        self.post_message(self.Focus(target_index=self._operation_index + 1))

    def focus(self, _: bool = True) -> Self:  # noqa: FBT001, FBT002
        def focus_first_focusable_button() -> None:
            buttons = self.query(CliveButton)
            for button in buttons:
                if button.focusable:
                    button.focus()
                    break

        focused = self.app.focused
        if not focused:
            return self

        assert focused.id, "Previously focused widget has no id!"
        try:
            previous = self.get_widget_by_id(focused.id, CliveButton)
        except NoMatches:
            focus_first_focusable_button()
            return self

        if previous.focusable:
            # Focus button that was focused before
            previous.focus()
        else:
            focus_first_focusable_button()
        return self

    @on(CliveButton.Pressed, "#move-up-button")
    def move_up(self) -> None:
        self._move("up")

    @on(CliveButton.Pressed, "#move-down-button")
    def move_down(self) -> None:
        self._move("down")

    @on(CliveButton.Pressed, "#delete-button")
    def delete(self) -> None:
        if self._action_manager.is_action_disabled:
            return

        self._action_manager.disable_action()
        self.post_message(self.Delete(self))

    @on(ButtonRawJson.Pressed)
    async def show_raw_json(self) -> None:
        await self.app.push_screen(RawJsonDialog(operation=self.operation))

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            CliveCheckerBoardTableCell(self.humanize_operation_number()),
            CliveCheckerBoardTableCell(self.humanize_operation_name(), classes="operation-name"),
            CliveCheckerBoardTableCell(self.humanize_operation_details(), classes="operation-details"),
            CliveCheckerBoardTableCell(self._create_buttons_container(), classes="actions"),
        ]

    def _create_buttons_container(self) -> Horizontal:
        button_move_up = ButtonMoveUp(disabled=self.is_first)
        button_move_down = ButtonMoveDown(disabled=self.is_last)
        button_delete = ButtonRemove()
        button_show_json = ButtonRawJson()
        return Horizontal(button_show_json, button_move_up, button_move_down, button_delete)

    def _is_operation_index_valid(self, value: int) -> bool:
        return value < self.operations_amount

    def _move(self, direction: Literal["up", "down"]) -> None:
        if self._action_manager.is_action_disabled:
            return
        self._action_manager.disable_action()
        index_change = -1 if direction == "up" else 1
        self.post_message(self.Move(from_index=self._operation_index, to_index=self._operation_index + index_change))


class CartHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("No.", classes=CLIVE_ODD_COLUMN_CLASS_NAME)
        yield Static("Operation type", classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} operation-name")
        yield Static("Operation details", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} operation-details")
        yield Static("Actions", classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} actions")


class CartTable(CliveCheckerboardTable):
    """Table with CartItems."""

    NO_CONTENT_TEXT = "Cart is empty"

    class Modified(Message):
        """Message sent when operations in CartTable were reordered or removed."""

    def __init__(self) -> None:
        super().__init__(header=CartHeader())
        self._cart_items_action_manager = CartItemsActionManager()

    @property
    def _cart_items(self) -> DOMQuery[CartItem]:
        return self.query(CartItem)

    @property
    def _has_cart_items(self) -> bool:
        return bool(self._cart_items)

    def create_static_rows(self) -> list[CartItem]:
        return [CartItem(index, self._cart_items_action_manager) for index in range(len(self.profile.cart))]

    @on(CartItem.Delete)
    async def remove_item(self, event: CartItem.Delete) -> None:
        item_to_remove = event.widget

        with self.app.batch_update():
            self._focus_appropriate_item_on_deletion(item_to_remove)
            await item_to_remove.remove()
            if self._has_cart_items:
                self._update_cart_items_on_deletion(removed_item=item_to_remove)
                self._disable_appropriate_button_on_deletion(removed_item=item_to_remove)
            else:
                await self.query_one(CartHeader).remove()
                await self.mount(NoContentAvailable(self.NO_CONTENT_TEXT))

        self.profile.cart.remove(item_to_remove.operation)
        self._cart_items_action_manager.enable_action()
        self.app.trigger_profile_watchers()
        self.post_message(self.Modified())

    @on(CartItem.Move)
    async def move_item(self, event: CartItem.Move) -> None:
        from_index = event.from_index
        to_index = event.to_index

        assert to_index >= 0, "Item cannot be moved to id lower than 0."
        assert to_index < len(self.profile.cart), "Item cannot be moved to id greater than cart length."

        with self.app.batch_update():
            self._update_values_of_swapped_rows(from_index=from_index, to_index=to_index)
            self._focus_item_on_move(to_index)

        self.profile.cart.swap(from_index, to_index)
        self._cart_items_action_manager.enable_action()
        self.app.trigger_profile_watchers()
        self.post_message(self.Modified())

    @on(CartItem.Focus)
    def focus_item(self, event: CartItem.Focus) -> None:
        for cart_item in self._cart_items:
            if event.target_index == cart_item.operation_index:
                cart_item.focus()

    def _update_cart_items_on_deletion(self, removed_item: CartItem) -> None:
        def update_indexes() -> None:
            for cart_item in cart_items_to_update:
                cart_item.operation_index = cart_item.operation_index - 1

        def update_operation_number() -> None:
            for cart_item in self._cart_items:
                cart_item.operation_number_cell.update_content(cart_item.humanize_operation_number(before_removal=True))

        start_index = removed_item.operation_index
        cart_items_to_update = self._cart_items[start_index:]
        update_indexes()
        update_operation_number()
        self._set_evenness_styles(cart_items_to_update, starting_index=start_index)

    def _disable_appropriate_button_on_deletion(self, removed_item: CartItem) -> None:
        if removed_item.is_first:
            self._cart_items.first().button_move_up.disabled = True
        elif removed_item.is_last:
            self._cart_items.last().button_move_down.disabled = True

    def _focus_appropriate_item_on_deletion(self, item_to_remove: CartItem) -> None:
        cart_items = self._cart_items
        if len(cart_items) < 2:  # noqa: PLR2004
            # There is no need for special handling, last one will be focused
            return

        if item_to_remove.is_last:
            second_last_cart_item_index = -2
            cart_item_to_focus = cart_items[second_last_cart_item_index]
        else:
            next_cart_item_index = item_to_remove.operation_index + 1
            cart_item_to_focus = cart_items[next_cart_item_index]

        cart_item_to_focus.focus()

    def _update_values_of_swapped_rows(self, from_index: int, to_index: int) -> None:
        def extract_cells_and_data(row_index: int) -> tuple[list[CliveCheckerBoardTableCell], list[str]]:
            row = self._cart_items[row_index]
            cells = row.query(CliveCheckerBoardTableCell)[1:-1]  # Skip "operation number" and "buttons container" cells
            data: list[str] = []
            for cell in cells:
                content = cell.content
                assert isinstance(content, str), f"Cell content is not a string: {content}"
                data.append(content)
            return list(cells), data

        def swap_cell_data(source_cells: list[CliveCheckerBoardTableCell], target_data: list[str]) -> None:
            for cell, value in zip(source_cells, target_data):
                cell.update_content(value)

        from_cells, from_data = extract_cells_and_data(from_index)
        to_cells, to_data = extract_cells_and_data(to_index)

        swap_cell_data(to_cells, from_data)
        swap_cell_data(from_cells, to_data)

    def _focus_item_on_move(self, target_index: int) -> None:
        for cart_item in self._cart_items:
            if target_index == cart_item.operation_index:
                cart_item.focus()
                break


class TransactionSummary(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f3", "load_transaction_from_file", "Open transaction file"),
        Binding("f6", "broadcast", "Broadcast"),
        Binding("f2", "save_to_file", "Save to file"),
    ]
    BIG_TITLE = "transaction summary"

    transaction: Transaction | None = reactive(None)  # type: ignore[assignment]

    def __init__(self) -> None:
        super().__init__()
        self.run_worker(self._build_transaction())
        self._transaction_metadata_container = TransactionMetadataContainer(self.transaction)
        self._select_key = SelectKey()
        self._broadcast_button_exists = False

    def watch_transaction(self, value: Transaction) -> None:
        self._transaction_metadata_container.transaction = value

    @property
    def button_broadcast(self) -> CliveButton:
        return self.query_one(ButtonBroadcast)

    @property
    def button_save(self) -> CliveButton:
        return self.query_one(ButtonSave)

    def create_main_panel(self) -> ComposeResult:
        yield self._transaction_metadata_container
        with Horizontal(id="actions-container"):
            yield KeyHint("Sign with key:")
            yield self._select_key
            with Horizontal(id="button-container"):
                yield self._get_broadcast_or_open_transaction_button()
                yield ButtonSave()
        with ScrollablePart():
            yield CartTable()

    async def on_mount(self) -> None:
        self._transaction_metadata_container.compose()
        self.transaction = await self._build_transaction() if self.profile.cart else None
        await self._handle_action_buttons_and_bindings()

    @on(ButtonOpenTransactionFromFile.Pressed)
    def action_load_transaction_from_file(self) -> None:
        notify_text = "Loading transaction from file will clear current cart content." if self.profile.cart else None
        self.app.push_screen(SelectFile(notice=notify_text))

    @on(ButtonBroadcast.Pressed)
    async def action_broadcast(self) -> None:
        await self._broadcast()

    @on(ButtonSave.Pressed)
    def action_save_to_file(self) -> None:
        self.app.push_screen(SelectFileToSaveTransaction())

    @on(CartTable.Modified)
    async def transaction_modified(self) -> None:
        self.transaction = await self._build_transaction() if self.profile.cart else None
        await self._handle_action_buttons_and_bindings()

    @CliveScreen.try_again_after_unlock
    @on(SelectFileToSaveTransaction.Saved)
    async def save_to_file(self, event: SelectFileToSaveTransaction.Saved) -> None:
        file_path = event.file_path
        save_as_binary = event.save_as_binary
        should_be_signed = event.should_be_signed
        assert self.transaction is not None, "Transaction can't be None while saving to file."
        transaction = self.transaction.copy()
        try:
            transaction = (
                await self.commands.perform_actions_on_transaction(
                    content=transaction,
                    sign_key=self._get_key_to_sign() if should_be_signed else None,
                    force_unsign=not should_be_signed,
                    save_file_path=file_path,
                    force_save_format="bin" if save_as_binary else "json",
                )
            ).result_or_raise
        except CommandRequiresUnlockedModeError:
            raise  # reraise so try_again_after_unlock decorator can handle it
        except Exception as error:  # noqa: BLE001
            self.notify(f"Transaction save failed. Reason: {error}", severity="error")
            return
        self.notify(
            f"Transaction ({'binary' if save_as_binary else 'json'}) saved to [bold green]'{file_path}'[/]"
            f" {'(signed)' if transaction.is_signed() else ''}"
        )

    @on(SelectFile.Saved)
    async def load_transaction_from_file(self, event: SelectFile.Saved) -> None:
        file_path = event.file_path

        try:
            loaded_transaction = (await self.commands.load_transaction_from_file(path=file_path)).result_or_raise
        except LoadTransactionError as error:
            self.notify(f"Error occurred while loading transaction from file: {error}", severity="error")
            return
        self.transaction = loaded_transaction
        if not self.transaction.is_tapos_set():
            self.notify("TaPoS metadata was not set, updating automatically...")
            await self.commands.update_transaction_metadata(transaction=self.transaction)

        self.profile.cart.fill_from_transaction(self.transaction)
        self.app.trigger_profile_watchers()
        await self.query_one(CartTable).rebuild()

    @CliveScreen.try_again_after_unlock
    async def _broadcast(self) -> None:
        from clive.__private.ui.screens.dashboard import DashboardBase

        transaction = self.transaction
        assert transaction is not None, "Transaction can't be None while broadcasting."
        try:
            (
                await self.commands.perform_actions_on_transaction(
                    content=transaction,
                    sign_key=self._get_key_to_sign() if not transaction.is_signed() else None,
                    broadcast=True,
                )
            ).raise_if_error_occurred()
        except CommandRequiresUnlockedModeError:
            raise  # reraise so try_again_after_unlock decorator can handle it
        except Exception as error:  # noqa: BLE001
            self.notify(f"Transaction broadcast failed! Reason: {error}", severity="error")
            return
        self.profile.cart.clear()
        self.notify(f"Transaction with ID '{transaction.calculate_transaction_id()}' successfully broadcasted!")
        self.app.pop_screen_until(DashboardBase)

    async def _build_transaction(self) -> Transaction:
        transaction = (await self.commands.build_transaction(content=self.profile.cart)).result_or_raise
        self.transaction = transaction
        return transaction

    def _get_broadcast_or_open_transaction_button(self) -> ButtonBroadcast | ButtonOpenTransactionFromFile:
        if self.profile.cart:
            self._broadcast_button_exists = True
            return ButtonBroadcast()
        return ButtonOpenTransactionFromFile()

    def _get_key_to_sign(self) -> PublicKey:
        return self._select_key.value

    async def _handle_action_buttons_and_bindings(self) -> None:
        if not self.profile.cart:
            if self._broadcast_button_exists:
                await self.query_one(ButtonBroadcast).remove()
                self._broadcast_button_exists = False
                await self.query_one("#button-container").mount(ButtonOpenTransactionFromFile(), before=0)
            self.button_save.disabled = True
            self.unbind("f6")
            self.unbind("f2")
        elif self.button_save.disabled and self.profile.cart:
            await self.query_one(ButtonOpenTransactionFromFile).remove()
            await self.query_one("#button-container").mount(ButtonBroadcast(), before=0)
            self._broadcast_button_exists = True
            self.button_save.disabled = False
            self.bind(Binding("f6", "broadcast", "Broadcast"))
            self.bind(Binding("f2", "save_to_file", "Save to file"))
