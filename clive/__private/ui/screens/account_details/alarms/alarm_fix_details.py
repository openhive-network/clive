from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from clive.__private.core.alarms.specific_alarms import (
    ChangingRecoveryAccountInProgress,
    DecliningVotingRightsInProgress,
    GovernanceNoActiveVotes,
    GovernanceVotingExpiration,
    RecoveryAccountWarningListed,
)
from clive.__private.core.clive_import import get_clive
from clive.__private.ui.screens.operations import Governance
from clive.exceptions import CliveDeveloperError

if TYPE_CHECKING:
    from clive.__private.core.alarms.alarm import AnyAlarm

AlarmFixActionT = Callable[[], Any]

GOVERNANCE_TUI_ALARM_FIX_ACTION_TEXT: Final[str] = "You can do it through the governance screen:"


@dataclass(kw_only=True)
class AlarmFixDetails:
    fix_info: str
    "Explanation for the user on how to fix the alarm."
    fix_action_text: str = ""
    "Text to be placed above the fix button."
    fix_button_text: str = ""
    "Text to be placed inside the fix button."
    fix_action_cb: AlarmFixActionT | None = None

    @property
    def fix_action_cb_ensure(self) -> AlarmFixActionT:
        assert self.fix_action_cb is not None, "You are trying to fix an alarm using clive without passing fix action."
        return self.fix_action_cb

    @property
    def is_fixable(self) -> bool:
        return bool(self.fix_button_text and self.fix_action_text)


class DetailedAlarmNotFoundError(CliveDeveloperError):
    _MESSAGE = """
The alarm you want to display is not found in ALARM_FIX_DETAILS_MAP.
You can also refer to the `Alarm` documentation to see how to properly create an alarm to be displayed in TUI.
    """

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)


def get_detailed_alarm_fix_details(alarm: AnyAlarm) -> AlarmFixDetails:
    try:
        return ALARM_FIX_DETAILS_MAP[type(alarm)]
    except KeyError as error:
        raise DetailedAlarmNotFoundError from error


def push_governance_screen() -> None:
    app = get_clive().app_instance()
    app.push_screen(Governance())


ALARM_FIX_DETAILS_MAP: Final[dict[type[AnyAlarm], AlarmFixDetails]] = {
    GovernanceVotingExpiration: AlarmFixDetails(
        fix_info=GovernanceVotingExpiration.FIX_ALARM_INFO,
        fix_action_text=GOVERNANCE_TUI_ALARM_FIX_ACTION_TEXT,
        fix_button_text="Go to governance",
        fix_action_cb=push_governance_screen,
    ),
    RecoveryAccountWarningListed: AlarmFixDetails(fix_info=RecoveryAccountWarningListed.FIX_ALARM_INFO),
    DecliningVotingRightsInProgress: AlarmFixDetails(fix_info=DecliningVotingRightsInProgress.FIX_ALARM_INFO),
    ChangingRecoveryAccountInProgress: AlarmFixDetails(fix_info=ChangingRecoveryAccountInProgress.FIX_ALARM_INFO),
    GovernanceNoActiveVotes: AlarmFixDetails(
        fix_info=GovernanceNoActiveVotes.FIX_ALARM_INFO,
        fix_action_text=GOVERNANCE_TUI_ALARM_FIX_ACTION_TEXT,
        fix_button_text="Go to governance",
        fix_action_cb=push_governance_screen,
    ),
}
