from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

AlarmFixActionT = Callable[[], Any]


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
