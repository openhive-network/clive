from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import events, on
from textual.containers import Horizontal
from textual.css.query import NoMatches
from textual.message import Message
from textual.widgets import Header, Static
from textual.widgets._header import HeaderIcon as TextualHeaderIcon
from textual.widgets._header import HeaderTitle

from clive.__private.core.formatters.data_labels import NOT_AVAILABLE_LABEL
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.alarm_display import AlarmDisplay
from clive.__private.ui.widgets.buttons import OneLineButton, OneLineButtonUnfocusable
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.dynamic_widgets.dynamic_one_line_button import (
    DynamicOneLineButtonUnfocusable,
)
from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Mount

    from clive.__private.core.app_state import AppState
    from clive.__private.core.node.node import Node
    from clive.__private.core.profile import Profile


class HeaderIcon(TextualHeaderIcon, CliveWidget):
    DEFAULT_CSS = """
    HeaderIcon:hover {
        background: rgba(0, 0, 0 , 0.2);
    }
    """

    def on_mount(self, event: Mount) -> None:  # type: ignore[override]
        event.prevent_default()

        self.watch(self.app, "header_expanded", self.header_expanded_changed)
        self.tooltip = "Toggle header details"

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.icon = "-" if expanded else "+"

    def on_click(self) -> None:  # type: ignore[override]
        self.app.header_expanded = not self.app.header_expanded


class BlockDisplay(Horizontal, CliveWidget):
    def compose(self) -> ComposeResult:
        yield TitledLabel(
            "Block",
            obj_to_watch=self.world,
            attribute_name="node",
            first_try_callback=lambda: self.node.cached.is_online_status_known,
            callback=self._get_last_block,
        )

    def _get_last_block(self) -> str:
        if not self.node.cached.is_online_with_basic_info_available:
            return NOT_AVAILABLE_LABEL

        gdpo = self.node.cached.dynamic_global_properties_ensure
        block_num = gdpo.head_block_number
        block_time = gdpo.time.time()
        return f"{block_num} ({block_time} UTC)"


class CartStatus(DynamicOneLineButtonUnfocusable):
    DEFAULT_CSS = """
    CartStatus Button {
        background: $secondary-lighten-1 !important;

        &:hover {
            background: $secondary-darken-1 !important;
        }
    }
    """

    def __init__(self) -> None:
        super().__init__(obj_to_watch=self.world, attribute_name="profile", callback=self.cart_status_callback)
        self.tooltip = "Proceed to transaction summary"

    @staticmethod
    def cart_status_callback(profile: Profile) -> str:
        operation_amount = len(profile.cart)
        amount_text = (
            "empty" if operation_amount <= 0 else f"{operation_amount} op{'s' if operation_amount > 1 else ''}"
        )
        return f"Cart ({amount_text})"

    @on(OneLineButton.Pressed)
    async def go_to_transaction_summary(self) -> None:
        from clive.__private.ui.screens.transaction_summary import TransactionSummary

        if isinstance(self.app.screen, TransactionSummary):
            return

        transaction = (
            (await self.commands.build_transaction(content=self.profile.cart)).result_or_raise
            if self.profile.cart
            else None
        )
        await self.app.push_screen(TransactionSummary(transaction))


class DashboardButton(OneLineButtonUnfocusable):
    def __init__(self) -> None:
        super().__init__("Dashboard")
        self.tooltip = "Go back to dashboard"

    @on(OneLineButton.Pressed)
    def go_to_dashboard(self) -> None:
        from clive.__private.ui.screens.dashboard import Dashboard

        if isinstance(self.app.screen, Dashboard):
            return

        self.app.get_screen_from_current_stack(Dashboard).pop_until_active()


class WorkingAccountButton(DynamicOneLineButtonUnfocusable):
    def __init__(self) -> None:
        super().__init__(
            obj_to_watch=self.world,
            attribute_name="profile",
            callback=self.working_account_callback,
            variant="success-on-transparent",
        )

    @staticmethod
    async def working_account_callback(profile: Profile) -> str:
        return f"@{profile.accounts.working.name}" if profile.accounts.has_working_account else "<no working account>"

    @on(OneLineButton.Pressed)
    def switch_working_account(self) -> None:
        if not self._is_working_account_switch_allowed:
            return

        if not self.profile.accounts.has_tracked_accounts:
            self._push_add_tracked_account_screen()
            return
        self._push_switch_working_account_screen()

    @on(CliveScreen.Resumed)
    def determine_tooltip(self) -> None:
        if not self._is_working_account_switch_allowed:
            self.tooltip = "Go to the dashboard to modify working account"
            return

        if not self.profile.accounts.has_tracked_accounts:
            self.tooltip = "Add account"
            return

        self.tooltip = "Switch working account"

    @property
    def _is_working_account_switch_allowed(self) -> bool:
        return self._is_current_screen_dashboard or self._is_current_screen_account_management

    @property
    def _is_current_screen_dashboard(self) -> bool:
        from clive.__private.ui.screens.dashboard import Dashboard

        return isinstance(self.app.screen, Dashboard)

    @property
    def _is_current_screen_account_management(self) -> bool:
        from clive.__private.ui.screens.config.account_management import AccountManagement

        return isinstance(self.app.screen, AccountManagement)

    def _push_switch_working_account_screen(self) -> None:
        from clive.__private.ui.dialogs import SwitchWorkingAccountDialog

        self.app.push_screen(SwitchWorkingAccountDialog())

    def _push_add_tracked_account_screen(self) -> None:
        from clive.__private.ui.dialogs import AddTrackedAccountDialog

        self.app.push_screen(AddTrackedAccountDialog())


class LockStatus(DynamicOneLineButtonUnfocusable):
    UNLOCKED_LABEL: Final[str] = "UNLOCKED"

    class WalletLocked(Message):
        """Posted when the wallet is locked."""

    class WalletUnlocked(Message):
        """Posted when the wallet is unlocked."""

    def __init__(self) -> None:
        super().__init__(
            obj_to_watch=self.world,
            attribute_name="app_state",
            callback=self.mode_callback,
            id_="status-icon",
            variant="success",
        )
        self.tooltip = "Lock wallet"

    @property
    def is_locked(self) -> bool:
        return self.app_state.is_unlocked

    def mode_callback(self, app_state: AppState) -> str:
        if app_state.is_unlocked:
            self._wallet_to_unlocked_changed()
            return self.UNLOCKED_LABEL

        self._wallet_to_locked_changed()
        return ""  # LOCKED label is not shown

    @on(OneLineButton.Pressed)
    async def lock_wallet(self) -> None:
        await self.commands.lock()

    def _wallet_to_locked_changed(self) -> None:
        self.post_message(self.WalletLocked())

    def _wallet_to_unlocked_changed(self) -> None:
        self.post_message(self.WalletUnlocked())


class NodeStatus(DynamicOneLineButtonUnfocusable):
    class ChangeNodeAddress(Message):
        """Posted when the user wants to change the node address."""

    def __init__(self) -> None:
        super().__init__(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self._update_node_status,
            first_try_callback=lambda: self.node.cached.is_online_status_known,
        )
        self.tooltip = "Switch node address"

    def _update_node_status(self, node: Node) -> str:
        if not node.cached.online_or_none:
            self._widget.variant = "error-on-transparent"
            return "offline"

        self._widget.variant = "success-on-transparent"
        return "online"

    @on(OneLineButton.Pressed)
    async def post_message_to_change_node_address(self) -> None:
        from clive.__private.ui.dialogs.switch_node_address_dialog import SwitchNodeAddressDialog
        from clive.__private.ui.screens.config.switch_node_address.switch_node_address import SwitchNodeAddress

        if isinstance(self.app.screen, SwitchNodeAddressDialog | SwitchNodeAddress):
            return

        self.screen.post_message(self.ChangeNodeAddress())


class RightPart(Horizontal):
    """Right part of the header or expandable."""


class LeftPart(Horizontal):
    """Left part of the header or expandable."""


class Bar(Horizontal):
    DEFAULT_CSS = """
    Bar {
        background: $panel;
        height: 1;
    }
    """


class CliveRawHeader(Header, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        yield Bar()
        with Horizontal():
            yield HeaderTitle()

    def _on_click(self, event: events.Click) -> None:  # type: ignore[override]
        """
        Override this method to prevent expanding header on click.

        Default behavior of the textual header is to expand on click.
        We do not want behavior like that, so we had to override the `_on_click` method.
        """
        event.prevent_default()

    def on_mount(self, event: Mount) -> None:
        # >>> start workaround for query_one(HeaderTitle) raising NoMatches error when title reactive is updated right
        # after pop_screen happens
        def set_title() -> None:
            self.query_exactly_one(HeaderTitle).text = self.screen_title

        def set_sub_title() -> None:
            self.query_exactly_one(HeaderTitle).sub_text = self.screen_sub_title

        event.prevent_default()

        self.watch(self.app, "title", set_title)
        self.watch(self.app, "sub_title", set_sub_title)
        self.watch(self.screen, "title", set_title)
        self.watch(self.screen, "sub_title", set_sub_title)
        # <<< end workaround

        self.watch(self.app, "header_expanded", self.header_expanded_changed)

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.add_class("-tall") if expanded else self.remove_class("-tall")


class CliveHeader(CliveRawHeader):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        super().__init__()
        self._node_version = DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self._get_node_version,
            first_try_callback=lambda: self.node.cached.is_online_status_known,
            id_="node-type",
        )

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        with Bar(id="bar"):
            if not self.world.is_in_create_profile_mode:
                with LeftPart():
                    yield from self._create_left_part_bar()
                yield LockStatus()
            with RightPart():
                yield from self._create_right_part_bar()

        with Horizontal():
            with LeftPart():
                yield from self._create_left_part_expandable()
            yield HeaderTitle()
            with RightPart():
                yield from self._create_right_part_expandable()

    def on_mount(self, _: Mount) -> None:
        if not self.world.is_in_create_profile_mode:
            self.watch(self.world, "profile", self._update_alarm_display_showing)

    @on(LockStatus.WalletUnlocked)
    def change_state_to_unlocked(self) -> None:
        self.add_class("-unlocked")

    @on(LockStatus.WalletLocked)
    def change_state_to_locked(self) -> None:
        self.remove_class("-unlocked")

    def _create_left_part_bar(self) -> ComposeResult:
        yield DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="profile",
            callback=self._get_profile_name,
            id_="profile-name",
        )
        yield Static("/", id="separator")
        yield WorkingAccountButton()
        yield AlarmDisplay()

    def _create_right_part_bar(self) -> ComposeResult:
        if not self.world.is_in_create_profile_mode:
            yield DashboardButton()
            yield CartStatus()
        yield NodeStatus()

    def _create_left_part_expandable(self) -> ComposeResult:
        yield BlockDisplay()

    def _create_right_part_expandable(self) -> ComposeResult:
        yield DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self._get_node_address,
            id_="node-address-label",
        )
        yield self._node_version

    def _update_alarm_display_showing(self, profile: Profile) -> None:
        """Use to mount/remove the alarm display depends on the current working account."""
        try:
            left_part = self.query_exactly_one("#bar LeftPart", LeftPart)
        except NoMatches:
            # Probably due to a textual error, in some situations this widget is not present.
            # related issue: https://github.com/Textualize/textual/pull/4817
            return

        is_mounted = bool(self.query(AlarmDisplay))
        has_working_account = profile.accounts.has_working_account

        if has_working_account and not is_mounted:
            left_part.mount(AlarmDisplay())
        elif not has_working_account and is_mounted:
            left_part.query_exactly_one(AlarmDisplay).remove()

    @staticmethod
    def _get_node_address(node: Node) -> str:
        return str(node.address)

    @staticmethod
    def _get_profile_name(profile: Profile) -> str:
        return profile.name

    def _get_node_version(self, node: Node) -> str:
        def format_network_type(value: str) -> str:
            return f"({value})"

        if not node.cached.is_online_with_basic_info_available:
            self._node_version.add_class("-no-connection")
            return format_network_type("no connection")

        network_type = node.cached.network_type_ensure
        is_mainnet = network_type == "mainnet"
        self._node_version.remove_class("-no-connection")
        self._node_version.set_class(is_mainnet, "-mainnet")
        self._node_version.set_class(not is_mainnet, "-not-mainnet")
        return format_network_type(network_type)
