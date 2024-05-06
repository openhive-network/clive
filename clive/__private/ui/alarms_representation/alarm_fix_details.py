from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Final

from clive.__private.core.alarms.specific_alarms import GovernanceVotingExpiration
from clive.__private.core.clive_import import get_clive
from clive.__private.ui.operations import Governance

if TYPE_CHECKING:
    from clive.__private.core.alarms.alarm import AnyAlarm

AlarmFixActionT = Callable[[], Any]

GOVERNANCE_TUI_ALARM_FIX_TEXT: Final[str] = "You can do it through the governance screen:"


@dataclass(kw_only=True)
class AlarmFixDetails:
    fix_info: str
    fix_button_text: str = ""
    fix_action_cb: AlarmFixActionT | None = None

    @property
    def fix_action_cb_ensure(self) -> AlarmFixActionT:
        assert self.fix_action_cb is not None, "You are trying to fix an alarm using clive without passing fix action."
        return self.fix_action_cb

    @property
    def is_fixable(self) -> bool:
        return bool(self.fix_button_text)


def push_governance_screen() -> None:
    app = get_clive().app_instance()
    app.push_screen(Governance())


ALARM_FIX_DETAILS_MAP: Final[dict[type[AnyAlarm], AlarmFixDetails]] = {
    GovernanceVotingExpiration: AlarmFixDetails(
        fix_info=f"{GovernanceVotingExpiration.EXTENDED_ALARM_INFO}\n{GOVERNANCE_TUI_ALARM_FIX_TEXT}",
        fix_button_text="Go to governance",
        fix_action_cb=push_governance_screen,
    )
}
