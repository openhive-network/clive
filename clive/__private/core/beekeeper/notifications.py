from __future__ import annotations

from asyncio import Event
from typing import Protocol

from clive.__private.core.beekeeper.notification_http_server import AsyncHttpServer, JsonT
from clive.__private.logger import logger
from clive.core.url import Url


class WalletClosingListener(Protocol):
    def notify_wallet_closing(self) -> None:
        ...


class BeekeeperNotificationsServer:
    def __init__(self) -> None:
        self.server = AsyncHttpServer(self)

        self.opening_beekeeper_failed = Event()
        self.http_listening_event = Event()
        self.ready = Event()
        self.http_endpoint: Url | None = None
        self.__wallet_closing_listeners: set[WalletClosingListener] = set()

    async def listen(self) -> int:
        await self.server.run()
        logger.debug(f"Notifications server is listening on {self.server.port}...")
        return self.server.port

    def notify(self, message: JsonT) -> None:
        logger.info(f"Got notification: {message}")
        details = message["value"]
        if message["name"] == "webserver listening":
            if details["type"] == "HTTP":
                self.http_endpoint = self.__parse_endpoint_notification(details)
                logger.debug(f"Got notification with http address on: {self.http_endpoint}")
                self.http_listening_event.set()
        elif message["name"] == "hived_status" and details["current_status"] == "signals attached":
            logger.debug("Beekeeper reports to be ready")
            self.ready.set()
        elif message["name"] == "opening_beekeeper_failed":
            details = details["connection"]
            assert details["type"] == "HTTP"
            self.http_endpoint = self.__parse_endpoint_notification(details)
            logger.debug(f"Got notification with http address, but beekeeper failed when opening: {self.http_endpoint}")
            self.opening_beekeeper_failed.set()
        elif message["name"] == "Attempt of closing all wallets":
            self.__notify_listeners_about_wallets_closing()

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

    def __notify_listeners_about_wallets_closing(self) -> None:
        logger.debug("Notifying listeners about wallets closing")
        for listener in self.__wallet_closing_listeners:
            listener.notify_wallet_closing()
