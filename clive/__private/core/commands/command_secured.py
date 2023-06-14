from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.commands.command import (
    Command,
    CommandT,
)
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState


PasswordResultCallbackT = Callable[[str], None]
ConfirmationCallbackT = Callable[[PasswordResultCallbackT, str], None]
ConfirmationCallbackOptionalT = ConfirmationCallbackT | None


@dataclass(kw_only=True)
class CommandSecured(Command[CommandT], ABC):
    """
    A command that requires a password to proceed.
    """

    confirmation_callback: ClassVar[ConfirmationCallbackOptionalT] = None

    app_state: AppState
    action_name: str = field(init=False)
    _password: str = field(init=False, repr=False)

    @classmethod
    def register_confirmation_callback(cls, callback: ConfirmationCallbackT) -> None:
        cls.confirmation_callback = callback

    def execute(self) -> None:
        assert self.confirmation_callback is not None, "Confirmation callback must be registered!"
        self.confirmation_callback(self._on_confirmation_callback, self.action_name)

    def execute_with_result(self) -> CommandT:
        """Result is returned too fast - before confirmation result callback is called."""
        raise RuntimeError("This command cannot be executed with result!")

    def _on_confirmation_callback(self, result: str) -> None:
        if result:
            self._password = result
            assert self.app_state.is_active(), "App must be in active mode to execute command secured with password!"
            self._execute()
        else:
            self._notify_tui()

    def _notify_tui(self) -> None:
        Notification(f"Action '{self.action_name}' requires a password! Please try again...", category="error").show()
