from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from clive.__private.ui.account_details.alarms.alarm_info_screen.fix_alarm_info_widget import FixAlarmInfoWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.clive_checkerboard_table import (
    EVEN_CLASS_NAME,
    ODD_CLASS_NAME,
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.one_line_button import OneLineButton
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.storage.accounts import Account
    from clive.__private.ui.account_details.alarms.alarm_fix_details import AlarmFixDetails


class AlarmInfo(Vertical):
    """Stores alarm data and a description of how to fix it."""

    BORDER_TITLE = "ALARM INFO"


class AlarmDataHeader(Horizontal):
    def __init__(self, *columns: str) -> None:
        super().__init__()
        self._columns = columns

    def compose(self) -> ComposeResult:
        for evenness, column in enumerate(self._columns):
            yield Static(column, classes=EVEN_CLASS_NAME if evenness % 2 else ODD_CLASS_NAME)


class AlarmDataRow(CliveCheckerboardTableRow):
    def __init__(self, cells: Iterable[str]) -> None:
        super().__init__(*[CliveCheckerBoardTableCell(content=cell) for cell in cells])


class AlarmData(CliveCheckerboardTable):
    def __init__(self, alarm: AnyAlarm) -> None:
        self._alarm_titled_data = alarm.alarm_data_ensure.get_titled_data()
        super().__init__(
            title=Static(""),
            header=AlarmDataHeader(*self._alarm_titled_data.keys()),
        )

    def create_static_rows(self) -> list[AlarmDataRow]:
        return [AlarmDataRow(self._alarm_titled_data.values())]


class AlarmInfoScreen(ModalScreen[None]):
    """Modal screen containing information about the alarm and description of how to fix it."""

    BINDINGS = [Binding("escape,f3", "request_close", "Close")]

    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, alarm: AnyAlarm, alarm_fix_details: AlarmFixDetails, account: Account) -> None:
        super().__init__()
        self._alarm = alarm
        self._alarm_fix_details = alarm_fix_details
        self._account = account

    def compose(self) -> ComposeResult:
        with AlarmInfo():
            yield SectionTitle.red(self._alarm.get_alarm_basic_info())
            yield SectionTitle("Details")
            if self._alarm.EXTENDED_ALARM_INFO:
                yield Static(self._alarm.EXTENDED_ALARM_INFO, id="extended-alarm-info")
            yield AlarmData(alarm=self._alarm)
            yield FixAlarmInfoWidget(
                alarm=self._alarm, alarm_fix_details=self._alarm_fix_details, account=self._account
            )
            with Container(id="close-button-container"):
                yield OneLineButton("Close", variant="error", id_="close-button")

    @on(OneLineButton.Pressed, "#close-button")
    def action_request_close(self) -> None:
        self.app.pop_screen()
