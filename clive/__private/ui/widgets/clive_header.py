from __future__ import annotations

from typing import TYPE_CHECKING

from textual import events, on
from textual.containers import Center, Container, Horizontal
from textual.message import Message
from textual.reactive import var
from textual.widgets import Header, Static
from textual.widgets._header import HeaderIcon as TextualHeaderIcon
from textual.widgets._header import HeaderTitle

from clive.__private.core.formatters.data_labels import NOT_AVAILABLE_LABEL
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.alarm_display import AlarmDisplay
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.dynamic_widgets.dynamic_one_line_button import (
    DynamicOneLineButtonUnfocusable,
)
from clive.__private.ui.widgets.titled_label import TitledLabel
from clive.exceptions import CommunicationError

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
        super().__init__(id="icon")
        self.tooltip = "Toggle header details"

    def on_mount(self) -> None:
        self.watch(self.app, "header_expanded", self.header_expanded_changed)

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.icon = "-" if expanded else "+"

    def on_click(self) -> None:  # type: ignore[override]
        self.app.header_expanded = not self.app.header_expanded


class DynamicPropertiesClock(Horizontal, CliveWidget):
    last_update_trigger = var(default=False)
    """A value that is used to trigger a re-rendering of the last update time."""

    def compose(self) -> ComposeResult:
        self.set_interval(1, self.__trigger_last_update)

        yield TitledLabel(
            "Block",
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self.__get_last_block,
        )

    async def __get_last_block(self) -> str:
        gdpo = await self.node.cached.dynamic_global_properties_or_none
        if gdpo is None:
            return NOT_AVAILABLE_LABEL

        block_num = gdpo.head_block_number
        block_time = gdpo.time.time()
        self.__trigger_last_update()
        return f"{block_num} ({block_time} UTC)"

    def __trigger_last_update(self) -> None:
        self.last_update_trigger = not self.last_update_trigger


class WorkingAccountIcon(DynamicOneLineButtonUnfocusable):
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
        if not self._is_current_screen_dashboard:
            return

        from clive.__private.ui.account_list_management.common.add_tracked_account_screen import AddTrackedAccountScreen
        from clive.__private.ui.account_list_management.common.switch_working_account.switch_working_account_screen import (  # noqa: E501
            SwitchWorkingAccountScreen,
        )

        if not self.profile.accounts.has_tracked_accounts:
            self.app.push_screen(AddTrackedAccountScreen())
            return
        self.app.push_screen(SwitchWorkingAccountScreen())

    @on(CliveScreen.Resumed)
    def determine_tooltip(self) -> None:
        if not self._is_current_screen_dashboard:
            self.tooltip = "Go to the dashboard to modify working account"
            return

        if not self.profile.accounts.has_tracked_accounts:
            self.tooltip = "Add account"
            return

        self.tooltip = "Switch working account"

    @property
    def _is_current_screen_dashboard(self) -> bool:
        from clive.__private.ui.dashboard.dashboard_base import DashboardBase

        return isinstance(self.app.screen, DashboardBase)


class ModeIcon(DynamicOneLineButtonUnfocusable):
    class WalletLocked(Message):
        """Posted when the wallet is locked."""

    class WalletUnlocked(Message):
        """Posted when the wallet is unlocked."""

    def __init__(self) -> None:
        super().__init__(
            obj_to_watch=self.world,
            attribute_name="app_state",
            callback=self.mode_callback,
            id_="mode-icon",
        )

    @property
    def mode(self) -> str:
        return str(self._widget.label).lower()

    async def mode_callback(self, app_state: AppState) -> str:
        if app_state.is_unlocked:
            self._wallet_to_unlocked_changed()
            return "UNLOCKED"

        self._wallet_to_locked_changed()
        return "LOCKED"

    @on(OneLineButton.Pressed)
    async def change_wallet_state(self) -> None:
        from clive.__private.ui.unlock.unlock import Unlock

        if isinstance(self.app.screen, Unlock):
            return

        if self.mode == "unlocked":
            await self.commands.lock()
            return

        await self.app.push_screen(Unlock())

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
            first_try_callback=lambda: self.node.cached.online is not None,
            variant="success-on-transparent",
        )

    async def _update_node_status(self, node: Node) -> str:
        if self.world.is_in_onboarding_mode:
            self.tooltip = None
        else:
            self._widget.tooltip = "Switch node address"

        if not node.cached.online:
            self._widget.variant = "error-on-transparent"
            return "offline"

        self._widget.variant = "success-on-transparent"
        return "online"

    @on(OneLineButton.Pressed)
    async def push_select_node_address(self) -> None:
        from clive.__private.ui.set_node_address.set_node_address import SetNodeAddress

        if isinstance(self.app.screen, SetNodeAddress) or self.world.is_in_onboarding_mode:
            return

        await self.app.push_screen(SetNodeAddress())


class CliveHeader(Header, CliveWidget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        self._header_title = HeaderTitle()
        super().__init__()
        self.__node_version = DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node",
            callback=self.__get_node_version,
            id_="node-type",
        )
        self._current_working_account = self.profile.accounts.working_or_none

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

    def compose(self) -> ComposeResult:
        yield HeaderIcon()
        with Horizontal(id="bar"):
            if not self.world.is_in_onboarding_mode:
                yield DynamicLabel(
                    obj_to_watch=self.world,
                    attribute_name="profile",
                    callback=self.__get_profile_name,
                    id_="profile-name",
                )
                yield Static("/", id="separator")
                yield WorkingAccountIcon()
                yield AlarmDisplay()
                with Center():
                    yield ModeIcon()
            with Container(id="node-status-container"):
                yield NodeStatus()

        with Horizontal(id="expandable"):
            yield DynamicPropertiesClock()
            yield self._header_title
            yield DynamicLabel(
                obj_to_watch=self.world,
                attribute_name="node",
                callback=self.__get_node_address,
                id_="node-address-label",
            )
            yield self.__node_version

    @on(ModeIcon.WalletUnlocked)
    def change_state_to_unlocked(self) -> None:
        self.add_class("-unlocked")

    @on(ModeIcon.WalletLocked)
    def change_state_to_locked(self) -> None:
        self.remove_class("-unlocked")

    def header_expanded_changed(self, expanded: bool) -> None:  # noqa: FBT001
        self.add_class("-tall") if expanded else self.remove_class("-tall")

    def _on_click(self, event: events.Click) -> None:  # type: ignore[override]
        """
        Override this method to prevent expanding header on click.

        Default behavior of the textual header is to expand on click.
        We do not want behavior like that, so we had to override the `_on_click` method.
        """
        event.prevent_default()

    @staticmethod
    def __get_node_address(node: Node) -> str:
        return str(node.address)

    @staticmethod
    def __get_profile_name(profile: Profile) -> str:
        return profile.name

    async def __get_node_version(self, node: Node) -> str:
        class_to_switch = "-not-mainnet"

        try:
            network_type = await node.cached.network_type
        except CommunicationError:
            network_type = "no connection"

        if network_type == "mainnet":
            self.__node_version.remove_class(class_to_switch)
        else:
            self.__node_version.add_class(class_to_switch)
        return f"({network_type})"
