from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.command_line_args import ExportKeysWalletParams
    from clive.core.url import Url


class BeekeeperDefaults(BaseModel):
    DEFAULT_BACKTRACE: ClassVar[str] = "yes"
    DEFAULT_CONFIG: ClassVar[str | None] = "config.ini"
    DEFAULT_DATA_DIR: ClassVar[Path] = Path.home() / ".beekeeper"
    DEFAULT_DUMP_CONFIG: ClassVar[None] = None
    DEFAULT_EXPORT_KEYS_WALLET: ClassVar[ExportKeysWalletParams | None] = None
    DEFAULT_GENERATE_COMPLETIONS: ClassVar[None] = None
    DEFAULT_HELP: ClassVar[None] = None
    DEFAULT_LIST_PLUGINS: ClassVar[None] = None
    DEFAULT_LOG_JSON_RPC: ClassVar[Path | None] = None
    DEFAULT_NOTIFICATIONS_ENDPOINT: ClassVar[Url | None] = None
    DEFAULT_PLUGIN: ClassVar[str | None] = None
    DEFAULT_RPC_ENDPOINT: ClassVar[Url | None] = None
    DEFAULT_UNLOCK_TIMEOUT: ClassVar[int] = 900
    DEFAULT_VERSION: ClassVar[None] = None
    DEFAULT_WALLET_DIR: ClassVar[Path] = Path.cwd()
    DEFAULT_WEBSERVER_HTTPS_CERTIFICATE_FILE_NAME: ClassVar[Path | None] = None
    DEFAULT_WEBSERVER_HTTPS_ENDPOINT: ClassVar[Url | None] = None
    DEFAULT_WEBSERVER_HTTPS_KEY_FILE_NAME: ClassVar[Path | None] = None
    DEFAULT_WEBSERVER_HTTP_ENDPOINT: ClassVar[Url | None] = None
    DEFAULT_WEBSERVER_THREAD_POOL_SIZE: ClassVar[int] = 32
    DEFAULT_WEBSERVER_UNIX_ENDPOINT: ClassVar[Url | None] = None
    DEFAULT_WEBSERVER_WS_DEFLATE: ClassVar[int | None] = 0
    DEFAULT_WEBSERVER_WS_ENDPOINT: ClassVar[Url | None] = None
