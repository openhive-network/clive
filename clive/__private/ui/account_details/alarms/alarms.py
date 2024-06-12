from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Horizontal
from textual.widgets import Static, TabPane

from clive.__private.storage.accounts import Account, WorkingAccount
from clive.__private.ui.account_details.alarms.alarm_fix_details import get_detailed_alarm_fix_details
from clive.__private.ui.account_details.alarms.alarm_info_screen.alarm_info_screen import AlarmInfoScreen
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.one_line_button import OneLineButton
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.profile_data import ProfileData
    from clive.__private.core.world import TextualWorld
    from clive.__private.ui.account_details.alarms.alarm_fix_details import AlarmFixDetails


class AlarmsTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Alarm", classes=ODD_CLASS_NAME)
        yield Static("Action", classes=EVEN_CLASS_NAME)


class AlarmsTableRow(CliveCheckerboardTableRow):
    def __init__(self, alarm: AnyAlarm, alarm_fix_details: AlarmFixDetails, account: Account) -> None:
        super().__init__(
            CliveCheckerBoardTableCell(alarm.get_alarm_basic_info(), classes="basic-info-cell"),
            CliveCheckerBoardTableCell(OneLineButton("Info", id_="alarm-info-button")),
        )
        self._alarm = alarm
        self._alarm_fix_details = alarm_fix_details
        self._account = account

    @on(OneLineButton.Pressed, "#alarm-info-button")
    def push_alarm_info_screen(self) -> None:
        self.app.push_screen(AlarmInfoScreen(self._alarm, self._alarm_fix_details, self._account))


class AlarmsTable(CliveCheckerboardTable):
    ATTRIBUTE_TO_WATCH = "profile_data"

    def __init__(self, account: Account):
        super().__init__(title=SectionTitle("Manage alarms"), header=AlarmsTableHeader())
        self._account = account
        self._previous_alarms: list[AnyAlarm] | NotUpdatedYet = NotUpdatedYet()

    def get_no_content_available_widget(self) -> NoContentAvailable:
        return NoContentAvailable("Account has no alarms")

    @property
    def object_to_watch(self) -> TextualWorld:
        return self.app.world

    def check_if_should_be_updated(self, content: ProfileData) -> bool:
        account = self._get_actual_account_state(content)
        alarms = account.alarms.harmful_alarms
        return alarms != self._previous_alarms

    def create_dynamic_rows(self, content: ProfileData) -> list[AlarmsTableRow]:
        account = self._get_actual_account_state(content)

        return [
            AlarmsTableRow(alarm, get_detailed_alarm_fix_details(alarm), account)
            for alarm in account.alarms.harmful_alarms
        ]

    def is_anything_to_display(self, content: ProfileData) -> bool:
        if not self._get_actual_account_state(content).is_alarms_data_available:
            return False

        return bool(self._get_actual_account_state(content).alarms.harmful_alarms)

    def update_previous_state(self, content: ProfileData) -> None:
        account = self._get_actual_account_state(content)
        self._previous_alarms = account.alarms.harmful_alarms

    def _get_account_from_watched_accounts(self, content: ProfileData) -> Account:
        """Search for the account in the watched account and return matched account."""
        searched_account = None
        for account in content.watched_accounts:
            if account == self._account:
                searched_account = account
        assert searched_account is not None, f"Account {self._account} not found in watched accounts"
        return searched_account

    def _get_actual_account_state(self, content: ProfileData) -> Account:
        """Return the account with the actual state."""
        return (
            content.working_account
            if self.is_current_account_working
            else self._get_account_from_watched_accounts(content)
        )

    @property
    def is_current_account_working(self) -> bool:
        return isinstance(self._account, WorkingAccount)


class Alarms(TabPane, CliveWidget):
    """TabPane with all info about alarms."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    ALARM_TAB_PANE_TITLE: Final[str] = "Alarms"

    def __init__(self, account: Account):
        super().__init__(title=self.ALARM_TAB_PANE_TITLE)
        self._account = account

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield AlarmsTable(self._account)
