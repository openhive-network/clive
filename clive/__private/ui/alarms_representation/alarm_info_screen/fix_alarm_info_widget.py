from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual import on
from textual.containers import Container
from textual.widgets import Static

from clive.__private.storage.accounts import WorkingAccount
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.one_line_button import OneLineButton
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.alarms.alarm import Alarm
    from clive.__private.storage.accounts import Account
    from clive.__private.ui.alarms_representation.alarm_fix_details import AlarmFixDetails


class FixAlarmInfoWidget(CliveWidget, can_focus=True):
    """A widget with information on how to fix the alarm, and possibly a button to mark it as harmless or go to clive-fix."""

    DEFAULT_CSS = """
    FixAlarmInfoWidget {
        height: auto;

        Static {
            width: 1fr;
            text-align: center;
        }

        #harmless-mark-info {
            margin-top: 1;
        }

        .button-container {
            height: auto;
            align: center top;
        }
    }
    """

    def __init__(self, alarm: Alarm[Any, Any], alarm_fix_details: AlarmFixDetails, related_account: Account) -> None:
        super().__init__()
        self._alarm = alarm
        self._alarm_fix_details = alarm_fix_details
        self._related_account = related_account

    def compose(self) -> ComposeResult:
        if isinstance(self._related_account, WorkingAccount):
            # It is impossible to perform operations without a working account, so if the account is watched, it is not possible to fix the alarm
            yield SectionTitle("How to fix it?")
            yield Static(self._alarm_fix_details.fix_info)
            if self._alarm.is_fix_possible_using_clive:
                with Container(classes="button-container"):
                    yield OneLineButton(self._alarm_fix_details.fix_button_text, id_="fix-alarm-button")
        else:
            yield SectionTitle("This is a watched account so it is not possible to fix the alarm.")

        yield Static("You can also mark this alarm as harmless.", id="harmless-mark-info")
        with Container(classes="button-container"):
            yield OneLineButton("Mark as harmless", variant="success", id_="harmless-button")

    @on(OneLineButton.Pressed, "#harmless-button")
    def mark_alarm_as_harmless(self) -> None:
        self._alarm.is_harmless = True
        self.app.trigger_profile_data_watchers()
        self.app.pop_screen()

    @on(OneLineButton.Pressed, "#fix-alarm-button")
    def fix_alarm_action(self) -> None:
        self._alarm_fix_details.fix_action_cb_ensure()
