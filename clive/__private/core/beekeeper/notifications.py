from __future__ import annotations

from threading import Event

from clive.__private.core.beekeeper.notification_http_server import HttpServer, JsonT
from clive.__private.logger import logger
from clive.core.url import Url


class BeekeeperNotificationsServer:
    def __init__(self) -> None:
        self.server = HttpServer(self, name="NotificationsServer")

        self.http_listening_event = Event()
        self.ready = Event()
        self.http_endpoint: Url | None = None

    def listen(self) -> int:
        self.server.run()
        logger.debug(f"Notifications server is listening on {self.server.port}...")
        return self.server.port

    def notify(self, message: JsonT) -> None:
        logger.info(f"Got notification: {message}")
        details: dict[str, str] = message["value"]
        if message["name"] == "webserver listening":
            if details["type"] == "HTTP":
                endpoint = f'{details["address"].replace("0.0.0.0", "127.0.0.1")}:{details["port"]}'
                self.http_endpoint = Url.parse(endpoint, protocol="http")
                logger.debug(f"Got notification with http address on: {endpoint}")
                self.http_listening_event.set()
        elif message["name"] == "hived_status" and details["current_status"] == "signals attached":
            logger.debug("Beekeeper reports to be ready")
            self.ready.set()

        logger.info(f"Received message: {message}")

    def close(self) -> None:
        self.server.close()

        self.http_listening_event.clear()

        logger.debug("Notifications server closed")
