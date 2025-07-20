from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Center
from textual.widgets import Static

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import Account
    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.ui.screens.account_details.alarms.alarm_fix_details import AlarmFixDetails


class FixAlarmInfoWidget(CliveWidget):
    """
    Widget with information how to fix the alarm, and possibly a button to mark it as harmless or go to clive-fix.

    Attributes:
        DEFAULT_CSS: Default CSS styles for the widget.

    Args:
        alarm: The alarm to be fixed.
        alarm_fix_details: Details about how to fix the alarm.
        account: The account associated with the alarm.
    """

    DEFAULT_CSS = """
    FixAlarmInfoWidget {
        height: auto;

        Static {
            width: 1fr;
            text-align: center;
        }

        Center {
            height: auto;
        }

        #actions-section-title {
            margin-top: 1;
        }

        #fix-alarm-button, #change-to-working-info {
            margin-bottom: 1;
        }
    }
    """

    def __init__(self, alarm: AnyAlarm, alarm_fix_details: AlarmFixDetails, account: Account) -> None:
        super().__init__()
        self._alarm = alarm
        self._alarm_fix_details = alarm_fix_details
        self._account = account

    @property
    def _is_account_working(self) -> bool:
        return self.profile.accounts.is_account_working(self._account)

    def compose(self) -> ComposeResult:
        yield from self._get_how_to_fix_content()
        yield from self._get_actions_content()

    @on(OneLineButton.Pressed, "#harmless-button")
    def mark_alarm_as_harmless(self) -> None:
        from clive.__private.ui.dialogs import MarkAlarmAsHarmlessDialog

        self.app.push_screen(MarkAlarmAsHarmlessDialog(self._alarm))

    @on(OneLineButton.Pressed, "#fix-alarm-button")
    def fix_alarm_action(self) -> None:
        self._alarm_fix_details.fix_action_cb_ensure()

    def _get_how_to_fix_content(self) -> ComposeResult:
        yield SectionTitle("How to fix it?")
        yield Static(self._alarm_fix_details.fix_info)

    def _get_mark_as_harmless_content(self) -> ComposeResult:
        yield Static("You can mark this alarm as harmless:")
        with Center():
            yield OneLineButton("Mark as harmless", variant="success", id_="harmless-button")

    def _get_actions_content(self) -> ComposeResult:
        yield SectionTitle("Actions", id_="actions-section-title")
        if not self._alarm_fix_details.is_fixable:
            yield from self._get_mark_as_harmless_content()
            return

        if self._is_account_working:
            # It is impossible to perform operations when account is not working,
            # so if the account is watched, it is not possible to go to screen with fix.
            yield Static(self._alarm_fix_details.fix_action_text)
            with Center():
                yield OneLineButton(self._alarm_fix_details.fix_button_text, id_="fix-alarm-button")
        else:
            yield Static(
                "You can change this account to a working one and fix the alarm with clive.",
                id="change-to-working-info",
            )
        yield from self._get_mark_as_harmless_content()
