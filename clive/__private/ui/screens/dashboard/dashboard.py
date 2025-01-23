from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final, Literal

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Label, Static

from clive.__private.core.accounts.accounts import TrackedAccount, WorkingAccount
from clive.__private.core.formatters.data_labels import MISSING_API_LABEL
from clive.__private.core.formatters.humanize import (
    humanize_datetime,
    humanize_hive_power,
    humanize_manabar_regeneration_time,
    humanize_percent,
)
from clive.__private.models import Asset
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import AddTrackedAccountDialog, SwitchWorkingAccountDialog
from clive.__private.ui.dialogs.liquid_navigation_dialog import LiquidNavigationDialog, auto_switch_working_account
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.account_details.account_details import AccountDetails
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.config import Config
from clive.__private.ui.screens.operations import Operations, Savings
from clive.__private.ui.widgets.alarm_display import AlarmDisplay
from clive.__private.ui.widgets.buttons import OneLineButton, OneLineButtonUnfocusable
from clive.__private.ui.widgets.dynamic_widgets.dynamic_one_line_button import (
    DynamicOneLineButtonUnfocusable,
)
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.tracked_account_referencing_widget import TrackedAccountReferencingWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.core.app_state import AppState
    from clive.__private.core.commands.data_retrieval.update_node_data import Manabar
    from clive.__private.core.profile import Profile
    from clive.__private.ui.widgets.buttons.clive_button import CliveButtonVariant


class Body(ScrollableContainer, can_focus=True):
    """A body for working/watched accounts container."""


class AccountsContainer(Container):
    """Container with working and watched accounts."""


class ManabarRepresentation(TrackedAccountReferencingWidget, CliveWidget):
    def __init__(
        self,
        account: TrackedAccount,
        manabar_type: Literal["rc_manabar", "vote_manabar", "downvote_manabar"],
        name: str,
        classes: str | None = None,
    ) -> None:
        self._manabar_type = manabar_type
        self.__name = name
        super().__init__(account=account, classes=classes)

    def compose(self) -> ComposeResult:
        yield self.create_dynamic_label(
            self._get_percentage_humanized,
            classes="percentage",
        )
        yield self.create_dynamic_label(
            self._get_hive_power_value_humanized,
            classes="hivepower-value",
        )
        yield self.create_dynamic_label(
            self.__get_regeneration_time,
            classes="time",
        )

    def _get_percentage_humanized(self) -> str:
        self._set_rc_api_missing()

        if self._is_rc_api_missing:
            return MISSING_API_LABEL

        return f"{humanize_percent(self.manabar.percentage)} {self.__name}"

    def _get_hive_power_value_humanized(self) -> str:
        if self._is_rc_api_missing:
            return MISSING_API_LABEL

        return humanize_hive_power(self.manabar.value)

    def __get_regeneration_time(self) -> str:
        if self._is_rc_api_missing:
            return MISSING_API_LABEL

        return humanize_manabar_regeneration_time(self.manabar.full_regeneration)

    def _set_rc_api_missing(self) -> None:
        """Set tooltip if rc api is missing."""
        if self._is_rc_api_missing:
            self.tooltip = self._account.data.rc_manabar_ensure_missing_api.missing_api_text
            return
        self.tooltip = None

    @property
    def _is_rc_api_missing(self) -> bool:
        return self._account.data.is_rc_api_missing and self._is_rc_current_manabar

    @property
    def _is_rc_current_manabar(self) -> bool:
        return self._manabar_type == "rc_manabar"

    @property
    def manabar(self) -> Manabar:
        return getattr(self._account.data, self._manabar_type)  # type: ignore[no-any-return]


class ManabarStats(TrackedAccountReferencingWidget):
    def compose(self) -> ComposeResult:
        yield ManabarRepresentation(self._account, "rc_manabar", "RC", classes="even-manabar")
        yield ManabarRepresentation(self._account, "vote_manabar", "VOTING", classes="odd-manabar")
        yield ManabarRepresentation(self._account, "downvote_manabar", "DOWNVOTING", classes="even-manabar")


class BalanceStatsButton(DynamicOneLineButtonUnfocusable):
    def __init__(
        self,
        account: TrackedAccount,
        balance_type: Literal["liquid", "savings"],
        asset_type: type[Asset.LiquidT],
        classes: str | None = None,
        variant: CliveButtonVariant = "primary",
    ) -> None:
        super().__init__(
            obj_to_watch=self.world,
            attribute_name="profile_reactive",
            callback=self._update_asset_value,
            first_try_callback=lambda: account.is_node_data_available,
            variant=variant,
            classes=classes,
        )
        self._balance_type = balance_type
        self._account = account
        self._asset_type = asset_type
        self._widget.add_class("balance-button")

        if balance_type == "savings":
            self.tooltip = f"Perform transfer from savings as {self._account.name}"
        else:
            self.tooltip = f"Choose liquid operation to perform as {self._account.name}"

    def _update_asset_value(self) -> str:
        asset_value = self._get_account_asset_value()
        return Asset.pretty_amount(asset_value)

    def _get_account_asset_value(self) -> Asset.LiquidT:
        asset_symbol = Asset.get_symbol(self._asset_type).lower()
        asset_name = f"{asset_symbol}_{self._balance_type}"

        asset_name_to_value: dict[str, Asset.LiquidT] = {
            "hive_liquid": self._account.data.hive_balance,
            "hive_savings": self._account.data.hive_savings,
            "hbd_liquid": self._account.data.hbd_balance,
            "hbd_savings": self._account.data.hbd_savings,
        }

        return asset_name_to_value[asset_name]

    @CliveScreen.prevent_action_when_no_accounts_node_data()
    @on(OneLineButton.Pressed, ".balance-button")
    def push_balance_screen(self) -> None:
        if self._balance_type == "liquid":
            self.app.push_screen(LiquidNavigationDialog(self._account, asset_type=self._asset_type))
            return

        auto_switch_working_account(self, self._account)
        self.app.push_screen(Savings("transfer-tab", "from-savings", self._asset_type))


class RemoveTrackedAccountButton(OneLineButtonUnfocusable, CliveWidget):
    """Used to remove account from the tracked list from the dashboard."""

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(
            "X",
            id_="remove-account-button",
            variant="error",
        )
        self._account = account
        self.tooltip = "Remove account from tracked"

    @on(OneLineButton.Pressed, "#remove-account-button")
    def _remove_account(self) -> None:
        self.profile.accounts.remove_tracked_account(self._account)
        self.app.trigger_profile_watchers()


class BalanceStats(TrackedAccountReferencingWidget):
    def compose(self) -> ComposeResult:
        yield Static("", classes="empty")
        yield EllipsedStatic("LIQUID", classes="title")
        yield EllipsedStatic("SAVINGS", classes="title title-variant")
        yield Static("HIVE", classes="token")
        yield BalanceStatsButton(self._account, "liquid", Asset.Hive, variant="grey-darken")
        yield BalanceStatsButton(self._account, "savings", Asset.Hive, variant="grey-lighten")
        yield Static("HBD", classes="token token-variant")
        yield BalanceStatsButton(self._account, "liquid", Asset.Hbd, variant="grey-lighten")
        yield BalanceStatsButton(self._account, "savings", Asset.Hbd, variant="grey-darken")


class TrackedAccountInfo(Container, TrackedAccountReferencingWidget):
    def compose(self) -> ComposeResult:
        with Vertical(id="account-alarms-and-details"):
            button = OneLineButton(f"{self._account.name}", id_="account-details-button")
            button.tooltip = "See account details"
            with Horizontal(id="details-remove-buttons-container"):
                yield button
                yield RemoveTrackedAccountButton(self._account)
            yield AlarmDisplay(self._account, id_="account-alarms")
        yield Label("LAST:")
        yield self.create_dynamic_label(
            lambda: f"History entry: {humanize_datetime(self._account.data.last_history_entry)}",
        )
        yield self.create_dynamic_label(
            lambda: f"Account update: {humanize_datetime(self._account.data.last_account_update)}",
        )

    @CliveScreen.prevent_action_when_no_accounts_node_data()
    @on(OneLineButton.Pressed, "#account-details-button")
    def push_account_details_screen(self) -> None:
        self.app.push_screen(AccountDetails(self._account))


class TrackedAccountRow(TrackedAccountReferencingWidget):
    def compose(self) -> ComposeResult:
        self.add_class("working" if isinstance(self._account, WorkingAccount) else "watched")
        with Horizontal():
            yield TrackedAccountInfo(self._account)
            with Container(id="tables"):
                yield ManabarStats(self._account)
                yield BalanceStats(self._account)


class WorkingAccountContainer(Static, CliveWidget):
    BORDER_TITLE = "WORKING ACCOUNT"

    def compose(self) -> ComposeResult:
        yield TrackedAccountRow(self.profile.accounts.working)


class WatchedAccountContainer(Static, CliveWidget):
    BORDER_TITLE = "WATCHED ACCOUNTS"

    def compose(self) -> ComposeResult:
        account_rows = [TrackedAccountRow(account) for account in self.profile.accounts.watched]
        last_account_row = account_rows[-1]
        last_account_row.add_class("last")
        yield from account_rows


class Dashboard(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__, name="dashboard")]
    _ADD_ACCOUNT_BINDING_KEY: Final[str] = "f4"
    NO_ACCOUNTS_INFO: ClassVar[str] = f"No accounts found (press {_ADD_ACCOUNT_BINDING_KEY} to add some)"

    BINDINGS = [
        Binding("f1", "help", "Help"),  # help is a hidden global binding, but we want to show it here
        Binding("f2", "operations", "Operations"),
        Binding("f3", "switch_working_account", "Switch working account"),
        Binding(_ADD_ACCOUNT_BINDING_KEY, "add_account", "Add account"),
        Binding("f5", "switch_mode_into_locked", "Lock wallet"),
        Binding("f6", "config", "Config"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._previous_tracked_accounts = self.tracked_accounts
        # used to check whether working or watched accounts have changed.

    def create_main_panel(self) -> ComposeResult:
        with Body(), AccountsContainer():
            if self.has_working_account:
                yield WorkingAccountContainer()
            if self.has_watched_accounts:
                yield WatchedAccountContainer()
            if not self.has_tracked_accounts:
                yield NoContentAvailable(self.NO_ACCOUNTS_INFO)

    def on_mount(self) -> None:
        self.watch(self.world, "profile_reactive", self._update_account_containers)
        self.watch(self.world, "app_state", self._update_mode)

    async def _update_account_containers(self, profile: Profile) -> None:
        if self.tracked_accounts == self._previous_tracked_accounts:
            return

        self._previous_tracked_accounts = profile.accounts.tracked

        widgets_to_mount: list[Widget] = []

        if self.has_working_account:
            widgets_to_mount.append(WorkingAccountContainer())

        if self.has_watched_accounts:
            widgets_to_mount.append(WatchedAccountContainer())

        if not self.has_tracked_accounts:
            widgets_to_mount.append(NoContentAvailable(self.NO_ACCOUNTS_INFO))

        with self.app.batch_update():
            accounts_container = self.query_exactly_one(AccountsContainer)
            await accounts_container.query("*").remove()
            await accounts_container.mount_all(widgets_to_mount)

    def _update_mode(self, app_state: AppState) -> None:
        self.is_unlocked = app_state.is_unlocked

    @CliveScreen.prevent_action_when_no_working_account()
    @CliveScreen.prevent_action_when_no_accounts_node_data()
    def action_operations(self) -> None:
        self.app.push_screen(Operations())

    def action_config(self) -> None:
        self.app.push_screen(Config())

    @CliveScreen.prevent_action_when_no_tracked_accounts()
    def action_switch_working_account(self) -> None:
        self.app.push_screen(SwitchWorkingAccountDialog())

    def action_add_account(self) -> None:
        self.app.push_screen(AddTrackedAccountDialog())

    async def action_switch_mode_into_locked(self) -> None:
        await self.app.world.commands.lock()

    @property
    def has_working_account(self) -> bool:
        return self.profile.accounts.has_working_account

    @property
    def has_watched_accounts(self) -> bool:
        return bool(self.profile.accounts.watched)

    @property
    def tracked_accounts(self) -> list[TrackedAccount]:
        return self.profile.accounts.tracked

    @property
    def has_tracked_accounts(self) -> bool:
        return self.has_working_account or self.has_watched_accounts
