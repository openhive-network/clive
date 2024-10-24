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
from clive.__private.ui.widgets.buttons import OneLineButton
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

    def __init__(self) -> None:
        super().__init__()
        self.tooltip = "Toggle header details"

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.header_expanded_changed)

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
    LOCKED_LABEL: Final[str] = "LOCKED"
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
        )

    @property
    def is_locked(self) -> bool:
        return str(self._widget.label) == self.LOCKED_LABEL

    def mode_callback(self, app_state: AppState) -> str:
        if app_state.is_unlocked:
            self._wallet_to_unlocked_changed()
            return self.UNLOCKED_LABEL

        self._wallet_to_locked_changed()
        return self.LOCKED_LABEL

    @on(OneLineButton.Pressed)
    async def change_wallet_status(self) -> None:
        from clive.__private.ui.screens.unlock import Unlock

        if isinstance(self.app.screen, Unlock):
            return

        if self.is_locked:
            await self.app.push_screen(Unlock())
        else:
            await self.commands.lock()

    def _wallet_to_locked_changed(self) -> None:
        self.post_message(self.WalletLocked())
        self._widget.variant = "error"
        self.tooltip = "Unlock wallet"

    def _wallet_to_unlocked_changed(self) -> None:
        self.post_message(self.WalletUnlocked())
        self._widget.variant = "success"
        self.tooltip = "Lock wallet"


class NodeStatus(DynamicOneLineButtonUnfocusable):
    def __init__(self) -> None:
        super().__init__(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self._update_node_status,
            first_try_callback=lambda: self.node.cached.is_online_status_known,
        )

    def _update_node_status(self, node: Node) -> str:
        if self.world.is_in_onboarding_mode:
            self.tooltip = None
        else:
            self._widget.tooltip = "Switch node address"

        if not node.cached.online_or_none:
            self._widget.variant = "error-on-transparent"
            return "offline"

        self._widget.variant = "success-on-transparent"
        return "online"

    @on(OneLineButton.Pressed)
    async def push_select_node_address(self) -> None:
        from clive.__private.ui.screens.config.set_node_address.set_node_address import SetNodeAddress

        if isinstance(self.app.screen, SetNodeAddress) or self.world.is_in_onboarding_mode:
            return

        await self.app.push_screen(SetNodeAddress())


class RightPart(Horizontal):
    """Right part of the header or expandable."""


class LeftPart(Horizontal):
    """Left part of the header or expandable."""


class CliveHeader(Header, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        self._header_title = HeaderTitle()
        super().__init__()
        self._node_version = DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self._get_node_version,
            first_try_callback=lambda: self.node.cached.is_online_status_known,
            id_="node-type",
        )

    def on_mount(self, event: Mount) -> None:
        # >>> start workaround for query_one(HeaderTitle) raising NoMatches error when title reactive is updated right
        # after pop_screen happens
        def set_title() -> None:
            self._header_title.text = self.screen_title

        def set_sub_title() -> None:
            self._header_title.sub_text = self.screen_sub_title

        event.prevent_default()

        self.watch(self.app, "title", set_title)
        self.watch(self.app, "sub_title", set_sub_title)
        self.watch(self.screen, "title", set_title)
        self.watch(self.screen, "sub_title", set_sub_title)
        # <<< end workaround

        self.watch(self.app, "header_expanded", self.header_expanded_changed)

        if not self.world.is_in_onboarding_mode:
            self.watch(self.world, "profile", self._update_alarm_display_showing)

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        with Horizontal(id="bar"):
            if not self.world.is_in_onboarding_mode:
                with LeftPart():
                    yield from self._create_left_part_bar()
                yield LockStatus()
            with RightPart():
                yield from self._create_right_part_bar()

        with Horizontal(id="expandable"):
            with LeftPart():
                yield from self._create_left_part_expandable()
            yield self._header_title
            with RightPart():
                yield from self._create_right_part_expandable()

    @on(LockStatus.WalletUnlocked)
    def change_state_to_unlocked(self) -> None:
        self.add_class("-unlocked")

    @on(LockStatus.WalletLocked)
    def change_state_to_locked(self) -> None:
        self.remove_class("-unlocked")

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.add_class("-tall") if expanded else self.remove_class("-tall")

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

    def _on_click(self, event: events.Click) -> None:  # type: ignore[override]
        """
        Override this method to prevent expanding header on click.

        Default behavior of the textual header is to expand on click.
        We do not want behavior like that, so we had to override the `_on_click` method.
        """
        event.prevent_default()

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
