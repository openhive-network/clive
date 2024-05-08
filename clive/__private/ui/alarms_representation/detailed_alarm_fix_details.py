from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from clive.__private.core.alarms.specific_alarms import GovernanceVotingExpiration, RecoveryAccountWarningListed
from clive.__private.core.clive_import import get_clive
from clive.__private.ui.alarms_representation.alarm_fix_details import AlarmFixDetails
from clive.__private.ui.operations import Governance

if TYPE_CHECKING:
    from clive.__private.core.alarms.alarm import Alarm

GOVERNANCE_TUI_ALARM_FIX_TEXT: Final[str] = "You can do it through the governance screen:"


def push_governance_screen() -> None:
    app = get_clive().app_instance()
    app.push_screen(Governance())


DETAILED_ALARM_FIX_DETAILS: Final[dict[type[Alarm[Any, Any]], AlarmFixDetails]] = {
    GovernanceVotingExpiration: AlarmFixDetails(
        fix_info=GovernanceVotingExpiration.EXTENDED_ALARM_INFO + GOVERNANCE_TUI_ALARM_FIX_TEXT,
        fix_button_text="Go to governance",
        fix_action_cb=push_governance_screen,
    ),
    RecoveryAccountWarningListed: AlarmFixDetails(fix_info=RecoveryAccountWarningListed.EXTENDED_ALARM_INFO),
}
