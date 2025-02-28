from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.dialogs.confirm_action_dialog import ConfirmActionDialog

if TYPE_CHECKING:
    from clive.__private.core.alarms.alarm import AnyAlarm


class MarkAlarmAsHarmlessDialog(ConfirmActionDialog):
    """Dialog to confirm if the user wants to mark alarm as harmless."""

    def __init__(self, alarm: AnyAlarm) -> None:
        self._alarm = alarm
        super().__init__(
            border_title="Marking the alarm as harmless",
            confirm_question=(
                f"You are about to mark `{self.alarm_info}` alarm as harmless.\nAre you sure you want to proceed?"
            ),
        )

    @property
    def alarm_info(self) -> str:
        return self._alarm.get_alarm_basic_info()

    @on(ConfirmActionDialog.Confirmed)
    def mark_alarm_as_harmless(self) -> None:
        self._alarm.is_harmless = True
        self.notify(f"Alarm `{self.alarm_info}` was marked as harmless.")
        self.app.trigger_profile_watchers()
        self.dismiss()
