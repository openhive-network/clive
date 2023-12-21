from __future__ import annotations

from asyncio import Event
from typing import TYPE_CHECKING, Any, Protocol

from clive.__private.core.beekeeper.notification_http_server import (
    AsyncHttpServer,
    JsonT,
)
from clive.__private.logger import logger
from clive.core.url import Url

if TYPE_CHECKING:
    from collections.abc import Callable


class WalletClosingListener(Protocol):
    def notify_wallet_closing(self) -> None:
        ...


class BeekeeperNotificationsServer:
    class BeekeeperNotificationsHandler:
        def __init__(self, beekeeper_ofitication_erver: BeekeeperNotificationsServer):
            self.beekeeperNotificationServer = beekeeper_ofitication_erver
            self.__notifications = {
                "webserver listening": self.__webserver_listening_notification,
                "hived_status": self.__hived_status_notification,
                "Opening beekeeper failed": self.__opening_beekeeper_failed_notification,
                "Attempt of closing all wallets": self.__attempt_of_closing_all_wallets_notification,
            }

        def notify(self, message: JsonT) -> None:
            name = message["name"]
            self.notification = self.__notifications.get(name, self.__unknown_notification)
            self.notification(message=message)

        def __webserver_listening_notification(self, message: JsonT) -> None:
            details = message["value"]
            if details["type"] == "HTTP":
                self.beekeeperNotificationServer.beekeeper_webserver_http_endpoint = self.__parse_endpoint_notification(
                    details
                )
                logger.debug(
                    "Got notification with webserver http address on:"
                    f" {self.beekeeperNotificationServer.beekeeper_webserver_http_endpoint}"
                )
                self.beekeeperNotificationServer.http_listening_event.set()
            else:
                logger.error(f'Received unsupported type : {details["type"]}')

        def __hived_status_notification(self, message: JsonT) -> None:
            details = message["value"]
            if details["current_status"] == "signals attached":
                logger.debug("Beekeeper reports to be ready")
                self.beekeeperNotificationServer.ready.set()
            elif details["current_status"] == "interrupted":
                logger.debug("Beekeeper has terminated.")
                self.beekeeperNotificationServer.terminated.set()
            elif details["current_status"] == "beekeeper is starting":
                logger.debug("Beekeeper is starting.")
            else:
                logger.error(f'Received unsupported hived_status : {details["current_status"]}')

        def __opening_beekeeper_failed_notification(self, message: JsonT) -> None:
            details = message["value"]
            details = details["connection"]
            assert details["type"] == "HTTP"
            self.beekeeperNotificationServer.beekeeper_webserver_http_endpoint = self.__parse_endpoint_notification(
                details
            )
            logger.debug(
                "Got notification with webserver http address, but beekeeper failed when opening:"
                f" {self.beekeeperNotificationServer.beekeeper_webserver_http_endpoint}"
            )
            self.beekeeperNotificationServer.opening_beekeeper_failed.set()

        def __attempt_of_closing_all_wallets_notification(self, message: JsonT) -> None:
            details = message["value"]
            logger.debug("Got notification about closing all wallets")
            if self.beekeeperNotificationServer._is_tracked_wallet_closing(details):
                self.beekeeperNotificationServer._notify_listeners_about_wallets_closing()
            else:
                logger.debug("The tracked wallet is not closing, ignoring notification")

        def __unknown_notification(self, message: JsonT) -> None:
            name = message["name"]
            logger.error(f"Received unsupported notification `{name}`.")

        @classmethod
        def __parse_endpoint_notification(cls, details: dict[str, str]) -> Url:
            return Url.parse(
                f"{details['address'].replace('0.0.0.0', '127.0.0.1')}:{details['port']}",
                protocol=details["type"].lower(),
            )

    def __init__(
        self, token_cb: Callable[[], str], notify_closing_wallet_name_cb: Callable[[], str] | None = None
    ) -> None:
        self.__token_cb = token_cb
        self.__notify_closing_wallet_name_cb = notify_closing_wallet_name_cb

        self.server = AsyncHttpServer(self)

        self.opening_beekeeper_failed = Event()
        self.http_listening_event = Event()
        self.ready = Event()
        self.terminated = Event()
        self.__beekeeper_webserver_http_endpoint_from_notification: Url | None = None
        self.__wallet_closing_listeners: set[WalletClosingListener] = set()
        self.__beekeeper_notification_handler = BeekeeperNotificationsServer.BeekeeperNotificationsHandler(self)

    @property
    def beekeeper_webserver_http_endpoint(self) -> Url:
        message = "Beekeeper webserver HTTP endpoint is not known yet"
        assert self.__beekeeper_webserver_http_endpoint_from_notification is not None, message
        return self.__beekeeper_webserver_http_endpoint_from_notification

    @beekeeper_webserver_http_endpoint.setter
    def beekeeper_webserver_http_endpoint(self, value: Url) -> None:
        self.__beekeeper_webserver_http_endpoint_from_notification = value

    @property
    def http_endpoint(self) -> Url:
        return self.server.address

    async def listen(self) -> Url:
        await self.server.run()
        logger.debug(f"Notifications server is listening on {self.server.port}...")
        return self.http_endpoint

    def notify(self, message: JsonT) -> None:
        logger.info(f"Got notification: {message}")
        self.__beekeeper_notification_handler.notify(message=message)

    async def close(self) -> None:
        await self.server.close()
        self.__clear_events()
        self.__beekeeper_webserver_http_endpoint_from_notification = None
        logger.debug("Notifications server closed")

    def __clear_events(self) -> None:
        self.opening_beekeeper_failed.clear()
        self.http_listening_event.clear()
        self.ready.clear()

    def attach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__wallet_closing_listeners.add(listener)

    def detach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__wallet_closing_listeners.discard(listener)

    def _is_tracked_wallet_closing(self, details: dict[str, Any]) -> bool:
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

    def _notify_listeners_about_wallets_closing(self) -> None:
        logger.debug("Notifying listeners about tracked wallet closing")
        for listener in self.__wallet_closing_listeners:
            listener.notify_wallet_closing()
