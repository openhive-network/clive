from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.abc.command_observable import CommandObservable

ActivationCallbackT = Callable[["CommandObservable"], None]
ActivationCallbackOptionalT = ActivationCallbackT | None

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState


@dataclass(kw_only=True)
class ActivateExtended(CommandObservable[bool]):
    activate_callback: ClassVar[ActivationCallbackOptionalT] = None

    app_state: AppState
    skip_activate: bool = False

    _is_armed: bool = field(init=False, default=True)  # nothing to set here, the command is always armed

    @classmethod
    def register_activate_callback(cls, callback: ActivationCallbackT) -> None:
        cls.activate_callback = callback

    def execute(self) -> None:
        assert self.activate_callback is not None, "The activate_callback is not set!"

        if not self.app_state.is_active():
            if self.skip_activate:
                raise RuntimeError("App is not in active mode and skip_activate is set to True.")
            self.activate_callback(self)
            return

        self.fire()

    def _execute(self) -> None:
        self._result = self.app_state.is_active()
