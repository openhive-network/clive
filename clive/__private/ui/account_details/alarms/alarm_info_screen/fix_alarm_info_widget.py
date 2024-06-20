from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from textual import on
from textual.containers import Center
from textual.widgets import Static

from clive.__private.storage.accounts import WorkingAccount
from clive.__private.ui.confirm_with_password.confirm_with_password import ConfirmWithPassword
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.one_line_button import OneLineButton
from clive.__private.ui.widgets.section_title import SectionTitle

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.core.alarms.alarm import AnyAlarm
    from clive.__private.storage.accounts import Account
    from clive.__private.ui.account_details.alarms.alarm_fix_details import AlarmFixDetails


class FixAlarmInfoWidget(CliveWidget):
    """Widget with information how to fix the alarm, and possibly a button to mark it as harmless or go to clive-fix."""

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

        #fix-alarm-button {
            margin-bottom: 1;
        }
    }
    """

    def __init__(self, alarm: AnyAlarm, alarm_fix_details: AlarmFixDetails, account: Account) -> None:
        super().__init__()
        self._alarm = alarm
        self._alarm_fix_details = alarm_fix_details
        self._account = account

    def compose(self) -> ComposeResult:
        yield from self._get_how_to_fix_content()
        yield from self._get_actions_content()

    @on(OneLineButton.Pressed, "#harmless-button")
    def mark_alarm_as_harmless(self) -> None:
        async def _on_confirmation_result(password: str) -> None:
            if not password:
                return

            self._alarm.is_harmless = True
            self.app.trigger_profile_data_watchers()
            self.app.pop_screen()

        self.app.push_screen(
            ConfirmWithPassword(
                result_callback=_on_confirmation_result,
                title=f"Marking alarm `{self._alarm.get_alarm_basic_info()}` as harmless",
            )
        )

    @on(OneLineButton.Pressed, "#fix-alarm-button")
    def fix_alarm_action(self) -> None:
        self._alarm_fix_details.fix_action_cb_ensure()

    def _get_how_to_fix_content(self) -> Iterable[Widget]:
        yield SectionTitle("How to fix it?")
        yield Static(self._alarm_fix_details.fix_info)

    def _get_actions_content(self) -> Iterable[Widget]:
        yield SectionTitle("Actions", id_="actions-section-title")
        if self._alarm_fix_details.is_fixable and isinstance(self._account, WorkingAccount):
            # It is impossible to perform operations without a working account,
            # so if the account is watched, it is not possible to go to screen with fix.
            yield Static(self._alarm_fix_details.fix_action_text)
            with Center():
                yield OneLineButton(self._alarm_fix_details.fix_button_text, id_="fix-alarm-button")
        yield Static("You can also mark this alarm as harmless:")
        with Center():
            yield OneLineButton("Mark as harmless", variant="success", id_="harmless-button")
