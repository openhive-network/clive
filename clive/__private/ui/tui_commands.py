from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.commands import Commands
from clive.__private.core.error_handlers.communication_failure_notificator import CommunicationFailureNotificator
from clive.__private.core.error_handlers.general_error_notificator import GeneralErrorNotificator
from clive.__private.core.error_handlers.tui_error_handler import TUIErrorHandler
from clive.__private.ui.clive_dom_node import CliveDOMNode

if TYPE_CHECKING:
    from textual.notifications import SeverityLevel

    from clive.__private.core.types import NotifyLevel
    from clive.__private.ui.tui_world import TUIWorld


class TUICommands(Commands["TUIWorld"], CliveDOMNode):
    def __init__(self, world: TUIWorld) -> None:
        super().__init__(
            world, exception_handlers=[TUIErrorHandler, CommunicationFailureNotificator, GeneralErrorNotificator]
        )

    def _notify(self, message: str, *, level: NotifyLevel = "info") -> None:
        clive_to_textual_notification_level: dict[NotifyLevel, SeverityLevel] = {
            "info": "information",
            "warning": "warning",
            "error": "warning",
        }
        assert level in clive_to_textual_notification_level, f"Unknown level: {level}"
        self.app.notify(message, severity=clive_to_textual_notification_level[level])
