from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Grid, Horizontal
from textual.widgets import Static

from clive.__private.core.formatters.data_labels import MISSING_API_LABEL
from clive.__private.core.formatters.humanize import humanize_operation_name, humanize_percent
from clive.__private.models import Asset
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.scrolling import ScrollablePartFocusable

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import WorkingAccount
    from clive.__private.core.profile import Profile
    from clive.__private.models.schemas import OperationBase


class Resources(Grid):
    """A grid that holds the resources info."""


class CartInfoContainer(Container):
    """A container that holds the label with amount of items and items itself."""


class CartItem(Static):
    """Holds the cart item info."""

    def __init__(self, index: int, operation: OperationBase) -> None:
        self._operation = operation
        super().__init__(f"{index}. {humanize_operation_name(operation)}")


class CartItemsAmount(DynamicLabel):
    """Holds the cart items amount info."""

    def __init__(self) -> None:
        super().__init__(self.world, "profile_reactive", self._get_cart_item_count)

    def _get_cart_item_count(self, profile: Profile) -> str:
        amount = len(profile.transaction)
        if amount > 0:
            return f"{amount} OPERATION{'S' if amount > 1 else ''} IN THE CART"
        return "CART IS EMPTY"


class CartItemsContainer(ScrollablePartFocusable):
    """A container that holds the cart items."""


class CartOverview(CliveWidget):
    def __init__(self) -> None:
        super().__init__()

        self._cart_items_container = CartItemsContainer()
        self._rc_container = Horizontal(id="rc-container")

    def compose(self) -> ComposeResult:
        with Resources():
            with self._rc_container:
                yield Static("RC:")
                yield DynamicLabel(self.world, "profile_reactive", self._get_rc)
            yield Static("HIVE balance:")
            yield DynamicLabel(
                self.world,
                "profile_reactive",
                self._get_hive_balance,
            )
            yield Static("HBD balance:")
            yield DynamicLabel(self.world, "profile_reactive", self._get_hbd_balance)
        with CartInfoContainer():
            yield CartItemsAmount()
            with self._cart_items_container:
                yield from self._create_cart_items(self.profile)

    def on_mount(self) -> None:
        self.watch(self.world, "profile_reactive", self._sync_cart_items)

    async def _sync_cart_items(self, profile: Profile) -> None:
        with self.app.batch_update():
            await self._cart_items_container.query(CartItem).remove()
            new_cart_items = self._create_cart_items(profile)
            await self._cart_items_container.mount(*new_cart_items)

    def _get_rc(self, profile: Profile) -> str:
        self._set_rc_api_missing(profile.accounts.working)
        if profile.accounts.working.data.is_rc_api_missing:
            return MISSING_API_LABEL

        return humanize_percent(profile.accounts.working.data.rc_manabar_ensure.percentage)

    def _set_rc_api_missing(self, working_account: WorkingAccount) -> None:
        if working_account.data.is_rc_api_missing:
            self._rc_container.tooltip = working_account.data.rc_manabar_ensure_missing_api.missing_api_text
            return

        self._rc_container.tooltip = None

    @staticmethod
    def _get_hive_balance(profile: Profile) -> str:
        return Asset.pretty_amount(profile.accounts.working.data.hive_balance)

    @staticmethod
    def _get_hbd_balance(profile: Profile) -> str:
        return Asset.pretty_amount(profile.accounts.working.data.hbd_balance)

    def _create_cart_items(self, profile: Profile) -> list[CartItem]:
        return [CartItem(index + 1, operation) for index, operation in enumerate(profile.transaction)]
