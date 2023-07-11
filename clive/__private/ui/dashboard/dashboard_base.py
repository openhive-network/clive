from __future__ import annotations

from typing import TYPE_CHECKING, Final

import humanize
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Label, Static

from clive.__private.storage.mock_database import Account, AccountType, Manabar, WorkingAccount
from clive.__private.ui.operations.operations import Operations
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.terminal.command_line import CommandLine
from clive.__private.ui.user_info.user_info import UserInfo
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.header import AlarmDisplay
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult


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

    def create_dynamic_label(self, foo: Callable[[], str], classes: str | None = None) -> DynamicLabel:
        return DynamicLabel(
            self.app.world,
            "profile_data",
            lambda _: foo() if self._account.name else "NULL",
            classes=classes,
        )


class ManabarRepresentation(AccountReferencingWidget, CliveWidget):
    def __init__(self, account: Account, manabar: Manabar, name: str, classes: str | None = None) -> None:
        self.__manabar = manabar
        self.__name = name
        super().__init__(account=account, classes=classes)

    def compose(self) -> ComposeResult:
        suppressed_units: Final[list[str]] = ["minutes", "seconds", "microseconds"]
        yield self.create_dynamic_label(
            lambda: f"{self.__manabar.percentage :.2f}% {self.__name}",
            classes="percentage",
        )
        yield self.create_dynamic_label(
            self.__pretty_hivepower,
            classes="hivepower-value",
        )
        yield self.create_dynamic_label(
            lambda: humanize.precisedelta(self.__manabar.full_regeneration, suppress=suppressed_units),
            classes="time",
        )

    def __pretty_hivepower(self) -> str:
        formated_size = humanize.naturalsize(self.__manabar.value, binary=False)
        return formated_size.replace(" Bytes", "").upper().replace(" ", "") + " HP"


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
            lambda: Asset.pretty_amount(self._account.data.hive_dollars),
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
            self.app.world, "profile_data", lambda _: f"Transaction: {self._account.data.last_transaction}"
        )
        yield DynamicLabel(self.app.world, "profile_data", lambda _: f"Update: {self._account.data.last_refresh}")


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
                yield CliveButton("account info", id_="account-info-button")
            yield CommandLine(focus_on_cancel=body)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "account-info-button":
            self.app.push_screen(UserInfo())
        else:
            Notification("Not implemented yet!", category="error").show()

    def action_operations(self) -> None:
        self.app.push_screen(Operations())
