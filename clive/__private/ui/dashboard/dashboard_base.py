from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Label, Static

from clive.__private.core.formatters.humanize import (
    humanize_datetime,
    humanize_hive_power,
    humanize_natural_time,
)
from clive.__private.storage.accounts import Account, AccountType, WorkingAccount
from clive.__private.ui.config.config import Config
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.operations import Operations
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.terminal.command_line import CommandLine
from clive.__private.ui.widgets.account_referencing_widget import AccountReferencingWidget
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.header import AlarmDisplay
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.models import Asset

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.storage.mock_database import Manabar


class Body(ScrollableContainer, can_focus=True):
    """A body for working/watched accounts container."""


class AccountsContainer(Container):
    """Container with working and watched accounts."""


class ManabarRepresentation(AccountReferencingWidget, CliveWidget):
    def __init__(self, account: Account, manabar: Manabar, name: str, classes: str | None = None) -> None:
        self.__manabar = manabar
        self.__name = name
        super().__init__(account=account, classes=classes)

    def compose(self) -> ComposeResult:
        yield self.create_dynamic_label(
            lambda: f"{self.__manabar.percentage :.2f}% {self.__name}",
            classes="percentage",
        )
        yield self.create_dynamic_label(
            lambda: humanize_hive_power(self.__manabar.value),
            classes="hivepower-value",
        )
        yield self.create_dynamic_label(
            self.__get_regeneration_time,
            classes="time",
        )

    def __get_regeneration_time(self) -> str:
        natural_time = humanize_natural_time(-self.__manabar.full_regeneration)
        return natural_time if natural_time != "now" else "Full!"


class BalanceStats(AccountReferencingWidget):
    full_caption: Final[str] = "full!"

    def compose(self) -> ComposeResult:
        yield ManabarRepresentation(self._account, self._account.data.rc_manabar, "RC", classes="even-manabar")
        yield ManabarRepresentation(self._account, self._account.data.vote_manabar, "VOTING", classes="odd-manabar")
        yield ManabarRepresentation(
            self._account, self._account.data.downvote_manabar, "DOWNVOTING", classes="even-manabar"
        )


class ActivityStats(AccountReferencingWidget):
    def compose(self) -> ComposeResult:
        yield Static("", classes="empty")
        yield EllipsedStatic("LIQUID", classes="title")
        yield EllipsedStatic("SAVINGS", classes="title title-variant")
        yield Static("HIVE", classes="token")
        yield self.create_dynamic_label(lambda: Asset.pretty_amount(self._account.data.hive_balance), "amount")
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hive_savings),
            "amount amount-variant",
        )
        yield Static("HBD", classes="token token-variant")
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hbd_balance),
            "amount amount-variant",
        )
        yield self.create_dynamic_label(
            lambda: Asset.pretty_amount(self._account.data.hbd_savings),
            "amount",
        )


class AccountInfo(Container, AccountReferencingWidget):
    def compose(self) -> ComposeResult:
        yield EllipsedStatic(f"{self._account.name}")
        yield AlarmDisplay(lambda _: [self._account], id_="account-alarms")
        yield Static()
        yield Label("LAST:")
        yield DynamicLabel(
            self.app.world,
            "profile_data",
            lambda: f"History entry: {humanize_datetime(self._account.data.last_history_entry)}",
        )
        yield DynamicLabel(
            self.app.world,
            "profile_data",
            lambda: f"Account update: {humanize_datetime(self._account.data.last_account_update)}",
        )


class AccountRow(AccountReferencingWidget):
    def compose(self) -> ComposeResult:
        self.add_class(AccountType.WORKING if isinstance(self._account, WorkingAccount) else AccountType.WATCHED)
        with Horizontal():
            yield AccountInfo(self._account)
            with Container(id="tables"):
                yield BalanceStats(self._account)
                yield Static()
                yield ActivityStats(self._account)


class WorkingAccountContainer(Static, CliveWidget):
    BORDER_TITLE = "WORKING ACCOUNT"

    def compose(self) -> ComposeResult:
        yield AccountRow(self.app.world.profile_data.working_account)


class WatchedAccountContainer(Static, CliveWidget):
    BORDER_TITLE = "WATCHED ACCOUNTS"

    def compose(self) -> ComposeResult:
        account_rows = [AccountRow(account) for account in self.app.world.profile_data.watched_accounts_sorted]
        last_account_row = account_rows[-1]
        last_account_row.add_class("last")
        yield from account_rows


class DashboardBase(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__, name="dashboard")]
    NO_ACCOUNTS_INFO: ClassVar[str] = "No accounts found (go to the Config view to add some)"

    BINDINGS = [
        Binding("colon", "focus('command-line-input')", "Command line", show=False),
        Binding("ctrl+o", "terminal", "Extend terminal", show=False),
        Binding("f1", "help", "Help"),  # help is a hidden global binding, but we want to show it here
        Binding("f2", "operations", "Operations"),
        Binding("f9", "config", "Config"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._previous_working_account = self.working_account
        self._previous_watched_accounts = self.watched_accounts
        # Both attributes are used to check whether working or watched accounts have changed.

    def create_main_panel(self) -> ComposeResult:
        with Body() as body:
            with AccountsContainer():
                if self.has_working_account:
                    yield WorkingAccountContainer()
                if self.has_watched_accounts:
                    yield WatchedAccountContainer()
                if not self.has_tracked_accounts:
                    yield NoContentAvailable(self.NO_ACCOUNTS_INFO)
            yield CommandLine(focus_on_cancel=body)

    def on_mount(self) -> None:
        self.watch(self.app.world, "profile_data", self._update_account_containers)

    async def _update_account_containers(self) -> None:
        if (
            self.working_account == self._previous_working_account
            and self.watched_accounts == self._previous_watched_accounts
        ):
            return

        self._previous_working_account = self.working_account
        self._previous_watched_accounts = self.watched_accounts

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

    def action_operations(self) -> None:
        if not self.has_working_account:
            self.notify("Cannot perform operations without working account", severity="error")
            return

        self.app.push_screen(Operations())

    def action_config(self) -> None:
        self.app.push_screen(Config())

    @property
    def has_working_account(self) -> bool:
        return self.app.world.profile_data.is_working_account_set()

    @property
    def has_watched_accounts(self) -> bool:
        return bool(self.app.world.profile_data.watched_accounts)

    @property
    def working_account(self) -> WorkingAccount | None:
        if not self.has_working_account:
            return None
        return self.app.world.profile_data.working_account

    @property
    def watched_accounts(self) -> set[Account]:
        return self.app.world.profile_data.watched_accounts.copy()

    @property
    def has_tracked_accounts(self) -> bool:
        return self.has_working_account or self.has_watched_accounts
