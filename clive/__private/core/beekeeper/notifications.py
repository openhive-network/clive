from __future__ import annotations

from asyncio import Event
from typing import TYPE_CHECKING, Any, Protocol

from clive.__private.core.beekeeper.notification_http_server import AsyncHttpServer, JsonT
from clive.__private.logger import logger
from clive.core.url import Url

if TYPE_CHECKING:
    from collections.abc import Callable


class WalletClosingListener(Protocol):
    def notify_wallet_closing(self) -> None:
        ...


class BeekeeperNotificationsServer:
    def __init__(
        self, token_cb: Callable[[], str], notify_closing_wallet_name_cb: Callable[[], str] | None = None
    ) -> None:
        self.__token_cb = token_cb
        self.__notify_closing_wallet_name_cb = notify_closing_wallet_name_cb

        self.server = AsyncHttpServer(self)

        self.opening_beekeeper_failed = Event()
        self.http_listening_event = Event()
        self.ready = Event()
        self.startup_token_available = Event()
        self.http_endpoint: Url | None = None
        self.startup_token: str | None = None
        self.__wallet_closing_listeners: set[WalletClosingListener] = set()

    async def listen(self) -> int:
        await self.server.run()
        logger.debug(f"Notifications server is listening on {self.server.port}...")
        return self.server.port

    def notify(self, message: JsonT) -> None:
        logger.info(f"Got notification: {message}")
        name = message["name"]
        details = message["value"]

        if name == "hived_status" and "starting a session with token" in details["current_status"]:
            self.startup_token = details["current_status"].split()[-1]
            self.startup_token_available.set()
        elif name == "webserver listening":
            if details["type"] == "HTTP":
                self.http_endpoint = self.__parse_endpoint_notification(details)
                logger.debug(f"Got notification with http address on: {self.http_endpoint}")
                self.http_listening_event.set()
        elif name == "hived_status" and details["current_status"] == "signals attached":
            logger.debug("Beekeeper reports to be ready")
            self.ready.set()
        elif name == "Opening beekeeper failed":
            details = details["connection"]
            assert details["type"] == "HTTP"
            self.http_endpoint = self.__parse_endpoint_notification(details)
            logger.debug(f"Got notification with http address, but beekeeper failed when opening: {self.http_endpoint}")
            self.opening_beekeeper_failed.set()
        elif name == "Attempt of closing all wallets":
            logger.debug("Got notification about closing all wallets")
            if self.__is_tracked_wallet_closing(details):
                self.__notify_listeners_about_wallets_closing()
            else:
                logger.debug("The tracked wallet is not closing, ignoring notification")

    @classmethod
    def __parse_endpoint_notification(cls, details: dict[str, str]) -> Url:
        return Url.parse(
            f"{details['address'].replace('0.0.0.0', '127.0.0.1')}:{details['port']}", protocol=details["type"].lower()
        )

    async def close(self) -> None:
        await self.server.close()

        self.http_listening_event.clear()

        logger.debug("Notifications server closed")

    def attach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__wallet_closing_listeners.add(listener)

    def detach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__wallet_closing_listeners.discard(listener)

    def __is_tracked_wallet_closing(self, details: dict[str, Any]) -> bool:
        if self.__notify_closing_wallet_name_cb is None:
            return False

        token = self.__token_cb()
        if token != details["token"]:
            logger.debug(f"Token mismatch in notification: {token} != {details['token']}")
            return False

        tracked_wallet_name = self.__notify_closing_wallet_name_cb()
        for wallet in details["wallets"]:
            if wallet["name"] != tracked_wallet_name:
                continue

            if not wallet["unlocked"]:
                logger.debug(f"The tracked wallet {tracked_wallet_name} is not unlocked, ignoring notification")
                return False
            return True

        return False

    def __notify_listeners_about_wallets_closing(self) -> None:
        logger.debug("Notifying listeners about tracked wallet closing")
        for listener in self.__wallet_closing_listeners:
            listener.notify_wallet_closing()
