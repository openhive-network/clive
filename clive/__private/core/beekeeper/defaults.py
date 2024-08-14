from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.command_line_args import ExportKeysWalletParams
    from clive.__private.core.url import Url


class BeekeeperDefaults(BaseModel):
    DEFAULT_HELP: ClassVar[bool] = False
    DEFAULT_VERSION: ClassVar[bool] = False
    DEFAULT_DUMP_CONFIG: ClassVar[bool] = False
    DEFAULT_BACKTRACE: ClassVar[str] = "yes"
    DEFAULT_DATA_DIR: ClassVar[Path] = Path.home() / ".beekeeper"
    DEFAULT_EXPORT_KEYS_WALLET: ClassVar[ExportKeysWalletParams | None] = None
    DEFAULT_LOG_JSON_RPC: ClassVar[Path | None] = None
    DEFAULT_NOTIFICATIONS_ENDPOINT: ClassVar[Url | None] = None
    DEFAULT_UNLOCK_TIMEOUT: ClassVar[int] = 900
    DEFAULT_UNLOCK_INTERVAL: ClassVar[int] = 500
    DEFAULT_WALLET_DIR: ClassVar[Path] = Path.cwd()
    DEFAULT_WEBSERVER_THREAD_POOL_SIZE: ClassVar[int] = 32
    DEFAULT_WEBSERVER_HTTP_ENDPOINT: ClassVar[Url | None] = None
