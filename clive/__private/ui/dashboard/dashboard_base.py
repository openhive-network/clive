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
    humanize_natural_time,
    humanize_percent,
)
from clive.__private.ui.account_details.account_details import AccountDetails
from clive.__private.ui.account_list_management.common.switch_working_account.switch_working_account_screen import (
    SwitchWorkingAccountScreen,
)
from clive.__private.ui.config.config import Config
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.operations import Operations
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.alarm_display import AlarmDisplay
from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.tracked_account_referencing_widget import TrackedAccountReferencingWidget
from clive.models import Asset

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.storage.mock_database import Manabar


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

        natural_time = humanize_natural_time(-self.manabar.full_regeneration)
        return natural_time if natural_time != "now" else "Full!"

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


class BalanceStats(TrackedAccountReferencingWidget):
    full_caption: Final[str] = "full!"

    def compose(self) -> ComposeResult:
        yield ManabarRepresentation(self._account, "rc_manabar", "RC", classes="even-manabar")
        yield ManabarRepresentation(self._account, "vote_manabar", "VOTING", classes="odd-manabar")
        yield ManabarRepresentation(self._account, "downvote_manabar", "DOWNVOTING", classes="even-manabar")


class ActivityStats(TrackedAccountReferencingWidget):
    def compose(self) -> ComposeResult:
        yield Static("", classes="empty")
        yield EllipsedStatic("LIQUID", classes="title")
        yield EllipsedStatic("SAVINGS", classes="title title-variant")
        yield Static("HIVE", classes="token")
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hive_balance),
            classes="amount",
        )
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hive_savings),
            classes="amount amount-variant",
        )
        yield Static("HBD", classes="token token-variant")
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hbd_balance),
            classes="amount amount-variant",
        )
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hbd_savings),
            classes="amount",
        )


class TrackedAccountInfo(Container, TrackedAccountReferencingWidget):
    def compose(self) -> ComposeResult:
        with Vertical(id="account-alarms-and-details"):
            button = OneLineButton(f"{self._account.name}", id_="account-details-button")
            button.tooltip = "See account details"
            yield button
            yield AlarmDisplay(self._account, id_="account-alarms")
        yield Static()
        yield Label("LAST:")
        yield self.create_dynamic_label(
            lambda: f"History entry: {humanize_datetime(self._account.data.last_history_entry)}",
        )
        yield self.create_dynamic_label(
            lambda: f"Account update: {humanize_datetime(self._account.data.last_account_update)}",
        )

    @CliveScreen.prevent_action_when_no_accounts_node_data
    @on(OneLineButton.Pressed, "#account-details-button")
    def push_account_details_screen(self) -> None:
        self.app.push_screen(AccountDetails(self._account))


class TrackedAccountRow(TrackedAccountReferencingWidget):
    def compose(self) -> ComposeResult:
        self.add_class("working" if isinstance(self._account, WorkingAccount) else "watched")
        with Horizontal():
            yield TrackedAccountInfo(self._account)
            with Container(id="tables"):
                yield BalanceStats(self._account)
                yield Static()
                yield ActivityStats(self._account)


class WorkingAccountContainer(Static, CliveWidget):
    BORDER_TITLE = "WORKING ACCOUNT"

    def compose(self) -> ComposeResult:
        yield TrackedAccountRow(self.profile_data.accounts.working)


class WatchedAccountContainer(Static, CliveWidget):
    BORDER_TITLE = "WATCHED ACCOUNTS"

    def compose(self) -> ComposeResult:
        account_rows = [TrackedAccountRow(account) for account in self.profile_data.accounts.watched]
        last_account_row = account_rows[-1]
        last_account_row.add_class("last")
        yield from account_rows


class DashboardBase(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__, name="dashboard")]
    NO_ACCOUNTS_INFO: ClassVar[str] = "No accounts found (go to the Config view to add some)"

    BINDINGS = [
        Binding("f1", "help", "Help"),  # help is a hidden global binding, but we want to show it here
        Binding("f2", "operations", "Operations"),
        Binding("f3", "switch_working_account", "Switch working account"),
        Binding("f9", "config", "Config"),
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
        self.watch(self.world, "profile_data", self._update_account_containers)

    async def _update_account_containers(self, profile_data: ProfileData) -> None:
        if self.tracked_accounts == self._previous_tracked_accounts:
            return

        self._previous_tracked_accounts = profile_data.accounts.tracked

        widgets_to_mount: list[Widget] = []

        if self.has_working_account:
            widgets_to_mount.append(WorkingAccountContainer())

        if self.has_watched_accounts:
            widgets_to_mount.append(WatchedAccountContainer())

        if not self.has_tracked_accounts:
            widgets_to_mount.append(NoContentAvailable(self.NO_ACCOUNTS_INFO))

        with self.app.batch_update():
            accounts_container = self.query_one(AccountsContainer)
            await accounts_container.query("*").remove()
            await accounts_container.mount_all(widgets_to_mount)

    @CliveScreen.prevent_action_when_no_accounts_node_data
    def action_operations(self) -> None:
        if not self.has_working_account:
            self.notify("Cannot perform operations without working account", severity="warning")
            return
        self.app.push_screen(Operations())

    def action_config(self) -> None:
        self.app.push_screen(Config())

    def action_switch_working_account(self) -> None:
        if not self.profile_data.accounts.tracked:
            self.notify("Cannot switch a working account without any account", severity="warning")
            return
        self.app.push_screen(SwitchWorkingAccountScreen())

    @property
    def has_working_account(self) -> bool:
        return self.profile_data.accounts.has_working_account

    @property
    def has_watched_accounts(self) -> bool:
        return bool(self.profile_data.accounts.watched)

    @property
    def tracked_accounts(self) -> list[TrackedAccount]:
        return self.profile_data.accounts.tracked

    @property
    def has_tracked_accounts(self) -> bool:
        return self.has_working_account or self.has_watched_accounts
