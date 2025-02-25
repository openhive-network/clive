from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from clive.__private.core.types import NotifyLevel

USER_WALLET_RECOVERED_NOTIFICATION_LEVEL: Final[NotifyLevel] = "warning"
USER_WALLET_RECOVERED_MESSAGE: Final[str] = (
    "Detected missing wallet. It was recovered, but keys can't be recovered. Please reimport them."
)
