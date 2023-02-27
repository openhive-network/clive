from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.widget import Widget
from textual.widgets import Label, Static

from clive.storage.mock_database import AccountType
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.ellipsed_static import EllipsedStatic

if TYPE_CHECKING:
    from textual.app import ComposeResult


class BalanceStats(Widget):
    def compose(self) -> ComposeResult:
        yield Static("RC", classes="title")
        yield EllipsedStatic("VOTING", classes="title title-variant")
        yield EllipsedStatic("DOWNVOTING", classes="title")
        yield EllipsedStatic("HIVEPOWER", classes="title title-variant")
        yield Static("75%", classes="percentage")
        yield Static("5d", classes="time")
        yield Static("65%", classes="percentage")
        yield Static("4d", classes="time")
        yield Static("55%", classes="percentage")
        yield Static("3d", classes="time")
        yield Static("170M", id="hivepower-value")


class ActivityStats(Widget):
    def compose(self) -> ComposeResult:
        yield Static("", classes="empty")
        yield EllipsedStatic("LIQUID", classes="title")
        yield EllipsedStatic("SAVINGS", classes="title title-variant")
        yield Static("HIVE", classes="token")
        yield Static("100.000", classes="amount")
        yield Static("100.000", classes="amount amount-variant")
        yield EllipsedStatic("HBD", classes="token token-variant")
        yield Static("100.000", classes="amount amount-variant")
        yield Static("100.000", classes="amount")


class AccountInfo(Container):
    def __init__(self, account_name: str, *, account_type: AccountType):
        super().__init__()
        self.__account_name = account_name
        self.__account_type = account_type

    def compose(self) -> ComposeResult:
        yield EllipsedStatic(f"{self.__account_type.capitalize()}: {self.__account_name}")
        yield Label("2x ALARMS!", id="account-alarms")
        yield Static()
        yield Label("LAST:")
        yield Label("Transaction: 10.01.23")
        yield Label("Update: 10.01.23")


class AccountRow(Container):
    def __init__(self, account_name: str, *, account_type: AccountType = AccountType.ACTIVE) -> None:
        super().__init__(classes=account_type)
        self.__account_name = account_name
        self.__account_type = account_type

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield AccountInfo(self.__account_name, account_type=self.__account_type)
            with Container(id="tables"):
                yield BalanceStats()
                yield Static()
                yield ActivityStats()


class DashboardBase(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        yield AccountRow("vogel")
        yield AccountRow("gtg", account_type=AccountType.WATCHED)
        yield AccountRow("veryverylonglongname", account_type=AccountType.WATCHED)
