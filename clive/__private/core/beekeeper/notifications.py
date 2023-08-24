from __future__ import annotations

from asyncio import Event
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar

from clive.__private.core.beekeeper.notification_http_server import AsyncHttpServer, JsonT
from clive.__private.logger import logger
from clive.core.url import Url

NotificationNameT = str
NotificationMessageT = dict[str, Any]
NotificationDetailsT = dict[str, Any]
NotificationHandlerT = Callable[[Any, NotificationMessageT], Any]
NotificationHandlerConditionT = Callable[[NotificationDetailsT], bool]

P = ParamSpec("P")
R = TypeVar("R")

PreWrapFuncT = Callable[[Any, NotificationDetailsT], R]
PostWrapFuncT = Callable[[Any, NotificationMessageT], R | None]


class NotificationDecorator(Protocol):
    def __call__(
        self, name_filter: NotificationNameT | None = None, *, condition: NotificationHandlerConditionT | None = None
    ) -> Callable[[PreWrapFuncT[R]], PostWrapFuncT[R]]:
        ...


def make_notification_decorator(
    handlers: set[NotificationHandlerT],
) -> NotificationDecorator:
    def notification(
        name_filter: NotificationNameT | None = None, *, condition: NotificationHandlerConditionT | None = None
    ) -> Callable[[PreWrapFuncT[R]], PostWrapFuncT[R]]:
        def decorator(
            func: PreWrapFuncT[R],
        ) -> PostWrapFuncT[R]:
            @wraps(func)
            def wrapper(this: BeekeeperNotificationsServer, message: NotificationMessageT) -> R | None:
                self = this
                assert isinstance(self, BeekeeperNotificationsServer)
                assert isinstance(message, dict)

                notification_name = message["name"]
                notification_details = message["value"]
                if name_filter is not None and name_filter != notification_name:
                    return None

                if condition is not None and not condition(notification_details):
                    return None

                return func(self, notification_details)

            handlers.add(wrapper)
            return wrapper

        return decorator

    return notification


class WalletClosingListener(Protocol):
    def notify_wallet_closing(self) -> None:
        ...


class BeekeeperNotificationsServer:
    _CLS_HANDLERS: set[NotificationHandlerT] = set()
    notification = make_notification_decorator(_CLS_HANDLERS)

    def __init__(
        self, token_cb: Callable[[], str], notify_closing_wallet_name_cb: Callable[[], str] | None = None
    ) -> None:
        self.__token_cb = token_cb
        self.__notify_closing_wallet_name_cb = notify_closing_wallet_name_cb

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

        for handler in self._CLS_HANDLERS:
            handler(self, message)

    @notification("webserver_listening", condition=lambda details: details["type"] == "HTTP")
    def handle_http_webserver_listening(self, _: NotificationDetailsT) -> None:
        logger.debug(f"Got notification with http address on: {self.http_endpoint}")
        self.http_listening_event.set()

    @notification("hived_status", condition=lambda details: details["current_status"] == "signals attached")
    def handle_signals_attached(self, _: NotificationDetailsT) -> None:
        logger.debug("Beekeeper reports to be ready")
        self.ready.set()

    @notification("opening_beekeeper_failed")
    def handle_opening_beekeeper_failed(self, details: NotificationDetailsT) -> None:
        details = details["connection"]
        assert details["type"] == "HTTP"
        self.http_endpoint = self.__parse_endpoint_notification(details)
        logger.debug(f"Got notification with http address, but beekeeper failed when opening: {self.http_endpoint}")
        self.opening_beekeeper_failed.set()

    @notification("Attempt of closing all wallets")
    def handle_attempt_closing_all_wallets_received(self, details: NotificationDetailsT) -> None:
        logger.debug("Got notification about closing all wallets")
        if not self.__is_tracked_wallet_closing(details):
            logger.debug("The tracked wallet is not closing, ignoring notification")
            return

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
