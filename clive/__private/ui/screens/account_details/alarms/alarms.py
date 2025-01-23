from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Horizontal
from textual.widgets import Static, TabPane

from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import AlarmInfoDialog
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.account_details.alarms.alarm_fix_details import get_detailed_alarm_fix_details
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.scrolling import ScrollablePart

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.core.profile import Profile
    from clive.__private.core.world import TUIWorld
    from clive.__private.ui.screens.account_details.alarms.alarm_fix_details import AlarmFixDetails


class AlarmsTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Alarm", classes=CLIVE_ODD_COLUMN_CLASS_NAME)
        yield Static("Action", classes=CLIVE_EVEN_COLUMN_CLASS_NAME)


class AlarmsTableRow(CliveCheckerboardTableRow):
    def __init__(self, alarm: AnyAlarm, alarm_fix_details: AlarmFixDetails, account: TrackedAccount) -> None:
        super().__init__(
            CliveCheckerBoardTableCell(alarm.get_alarm_basic_info(), classes="basic-info-cell"),
            CliveCheckerBoardTableCell(OneLineButton("Info", id_="alarm-info-button")),
        )
        self._alarm = alarm
        self._alarm_fix_details = alarm_fix_details
        self._account = account

    @on(OneLineButton.Pressed, "#alarm-info-button")
    def push_alarm_info_screen(self) -> None:
        self.app.push_screen(AlarmInfoDialog(self._alarm, self._alarm_fix_details, self._account))


class AlarmsTable(CliveCheckerboardTable):
    ATTRIBUTE_TO_WATCH = "profile_reactive"
    NO_CONTENT_TEXT = "Account has no alarms"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(header=AlarmsTableHeader(), title="Manage alarms")
        self._account = account
        self._previous_alarms: list[AnyAlarm] | NotUpdatedYet = NotUpdatedYet()

    @property
    def object_to_watch(self) -> TUIWorld:
        return self.world

    def check_if_should_be_updated(self, content: Profile) -> bool:
        account = self._get_actual_account_state(content)
        alarms = account.alarms.harmful_alarms
        return alarms != self._previous_alarms

    def create_dynamic_rows(self, content: Profile) -> list[AlarmsTableRow]:
        account = self._get_actual_account_state(content)

        return [
            AlarmsTableRow(alarm, get_detailed_alarm_fix_details(alarm), account)
            for alarm in account.alarms.harmful_alarms
        ]

    def is_anything_to_display(self, content: Profile) -> bool:
        if not self._get_actual_account_state(content).is_alarms_data_available:
            return False

        return bool(self._get_actual_account_state(content).alarms.harmful_alarms)

    def update_previous_state(self, content: Profile) -> None:
        account = self._get_actual_account_state(content)
        self._previous_alarms = account.alarms.harmful_alarms

    def _get_actual_account_state(self, content: Profile) -> TrackedAccount:
        """Return the account with the actual state."""
        return content.accounts.get_tracked_account(self._account)


class Alarms(TabPane, CliveWidget):
    """TabPane with all info about alarms."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    ALARM_TAB_PANE_TITLE: Final[str] = "Alarms"

    def __init__(self, account: TrackedAccount) -> None:
        super().__init__(title=self.ALARM_TAB_PANE_TITLE)
        self._account = account

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield AlarmsTable(self._account)
