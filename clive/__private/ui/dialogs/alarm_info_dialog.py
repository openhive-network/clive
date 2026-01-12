from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.constants.tui.class_names import CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME
from clive.__private.ui.dialogs.clive_base_dialogs import AutoDismissDialog, CliveInfoDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.account_details.alarms.fix_alarm_info_widget import FixAlarmInfoWidget
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.ui.screens.account_details.alarms.alarm_fix_details import AlarmFixDetails


class AlarmDataHeader(Horizontal):
    def __init__(self, *columns: str) -> None:
        super().__init__()
        self._columns = columns

    def compose(self) -> ComposeResult:
        for column in self._columns:
            yield Static(column, classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)


class AlarmDataRow(CliveCheckerboardTableRow):
    def __init__(self, cells: Iterable[str]) -> None:
        super().__init__(*[CliveCheckerBoardTableCell(content=cell) for cell in cells])


class AlarmData(CliveCheckerboardTable):
    def __init__(self, alarm: AnyAlarm) -> None:
        self._alarm_titled_data = alarm.alarm_data_ensure.get_titled_data()
        super().__init__(
            header=AlarmDataHeader(*self._alarm_titled_data.keys()),
        )

    def create_static_rows(self) -> list[AlarmDataRow]:
        return [AlarmDataRow(self._alarm_titled_data.values())]


class AlarmInfoDialog(AutoDismissDialog, CliveInfoDialog):
    """
    Dialog screen containing information about the alarm and description of how to fix it.

    Attributes:
        CSS_PATH: Path to the CSS file for styling the dialog.

    Args:
        alarm: The alarm object containing details about the alarm.
        alarm_fix_details: Details on how to fix the alarm.
        account: The account associated with the alarm.
    """

    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, alarm: AnyAlarm, alarm_fix_details: AlarmFixDetails, account: TrackedAccount) -> None:
        super().__init__(border_title=alarm.get_alarm_basic_info(), variant="error")
        self._alarm = alarm
        self._alarm_fix_details = alarm_fix_details
        self._account = account

    def create_dialog_content(self) -> ComposeResult:
        yield SectionTitle("Details")
        if self._alarm.ALARM_DESCRIPTION:
            yield Static(self._alarm.ALARM_DESCRIPTION, id="alarm-description")
        yield AlarmData(alarm=self._alarm)
        yield FixAlarmInfoWidget(alarm=self._alarm, alarm_fix_details=self._alarm_fix_details, account=self._account)
