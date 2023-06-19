from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Label, Static

from clive.__private.storage.mock_database import Account, AccountType, WorkingAccount
from clive.__private.ui.operations.operations import Operations
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.terminal.command_line import CommandLine
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.core.world import TextualWorld


class ContainerTitle(Static):
    """A title for working/watched accounts container"""


class Body(Static, can_focus=True):
    """A body for working/watched accounts container"""


class AccountReferencingWidget(CliveWidget):
    def __init__(
        self,
        account: Account,
        name: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._account = account
        super().__init__(name=name, classes=classes)


def create_dynamic_label(
    world: TextualWorld, account: Account, foo: Callable[[ProfileData, Account], str], classes: str | None = None
) -> DynamicLabel:
    return DynamicLabel(world, "profile_data", lambda pd: foo(pd, account) if account.name else "NULL", classes=classes)


class BalanceStats(AccountReferencingWidget):
    full_caption: Final[str] = "full!"

    def compose(self) -> ComposeResult:
        yield Static("RC", classes="title")
        yield EllipsedStatic("VOTING", classes="title title-variant")
        yield EllipsedStatic("DOWNVOTING", classes="title")
        yield EllipsedStatic("HIVEPOWER", classes="title title-variant")
        # RC
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: f"{acc.data.rc}%",
            "percentage",
        )
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: f"{acc.data.hours_until_full_refresh_rc}h"
            if acc.data.hours_until_full_refresh_rc
            else self.full_caption,
            "time",
        )

        # VOTING
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: f"{acc.data.voting_power}%",
            "percentage",
        )
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: f"{acc.data.hours_until_full_refresh_voting_power}h"
            if acc.data.hours_until_full_refresh_voting_power
            else self.full_caption,
            "time",
        )

        # DOWNVOTING
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: f"{acc.data.down_vote_power}%",
            "percentage",
        )
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: f"{acc.data.hours_until_full_refresh_downvoting_power}h"
            if acc.data.hours_until_full_refresh_downvoting_power
            else self.full_caption,
            "time",
        )

        # HIVEPOWER
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: f"{acc.data.hive_power_balance:_} HP".replace("_", " "),
            "hivepower-value",
        )


class ActivityStats(AccountReferencingWidget):
    def compose(self) -> ComposeResult:
        yield Static("", classes="empty")
        yield EllipsedStatic("LIQUID", classes="title")
        yield EllipsedStatic("SAVINGS", classes="title title-variant")
        yield Static("HIVE", classes="token")
        yield create_dynamic_label(
            self.app.world, self._account, lambda _, acc: Asset.pretty_amount(acc.data.hive_balance), "amount"
        )
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: Asset.pretty_amount(acc.data.hive_savings),
            "amount amount-variant",
        )
        yield Static("HBD", classes="token token-variant")
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: Asset.pretty_amount(acc.data.hive_dollars),
            "amount amount-variant",
        )
        yield create_dynamic_label(
            self.app.world,
            self._account,
            lambda _, acc: Asset.pretty_amount(acc.data.hbd_savings),
            "amount",
        )


class AccountInfo(Container, AccountReferencingWidget):
    def compose(self) -> ComposeResult:
        yield EllipsedStatic(f"{self._account.name}")
        yield Label("2x ALARMS!", id="account-alarms")
        yield Static()
        yield Label("LAST:")
        yield Label("Transaction: 10.01.23")
        yield DynamicLabel(self.app.world, "profile_data", lambda _: f"Update: {self._account.data.last_refresh}")


class AccountRow(Container):
    def __init__(self, account: Account) -> None:
        self.__account = account
        self.__account_type = AccountType.WORKING if isinstance(account, WorkingAccount) else AccountType.WATCHED
        super().__init__(classes=self.__account_type)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield AccountInfo(self.__account)
            with Container(id="tables"):
                yield BalanceStats(self.__account)
                yield Static()
                yield ActivityStats(self.__account)


class WorkingAccountContainer(Static, CliveWidget):
    def compose(self) -> ComposeResult:
        yield AccountRow(self.app.world.profile_data.working_account)


class WatchedAccountContainer(Static, CliveWidget):
    def compose(self) -> ComposeResult:
        for acc in self.app.world.profile_data.watched_accounts:
            yield AccountRow(acc)


class DashboardBase(BaseScreen):
    BINDINGS = [
        Binding("colon", "focus('command-line-input')", "Command line", show=False),
        Binding("ctrl+o", "terminal", "Extend terminal", show=False),
        Binding("f2", "operations", "Operations"),
    ]

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            with Body() as body:
                yield ContainerTitle("WORKING ACCOUNT", classes="working")
                yield WorkingAccountContainer()
                yield ContainerTitle("WATCHED ACCOUNTS", classes="watched")
                yield WatchedAccountContainer()
            yield CommandLine(focus_on_cancel=body)

    def action_operations(self) -> None:
        self.app.push_screen(Operations())
