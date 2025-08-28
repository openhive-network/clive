from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.commands import Commands
from clive.__private.core.error_handlers.communication_failure_notificator import CommunicationFailureNotificator
from clive.__private.core.error_handlers.general_error_notificator import GeneralErrorNotificator

if TYPE_CHECKING:
    from clive.__private.cli.cli_world import CLIWorld
    from clive.__private.core.types import NotifyLevel


class CLICommands(Commands["CLIWorld"]):
    def __init__(self, world: CLIWorld) -> None:
        super().__init__(world, exception_handlers=[CommunicationFailureNotificator, GeneralErrorNotificator])

    def _notify(self, message: str, *, level: NotifyLevel = "info") -> None:
        from clive.__private.cli.notify import notify  # noqa: PLC0415

        notify(message, level=level)
