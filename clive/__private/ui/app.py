from __future__ import annotations

import asyncio
import math
import traceback
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, TypeVar, cast

from helpy.exceptions import CommunicationError
from textual import on, work
from textual._context import active_app
from textual.app import App
from textual.binding import Binding
from textual.notifications import Notification, Notify, SeverityLevel
from textual.reactive import var

from clive.__private.core._async import asyncio_run
from clive.__private.core.constants.terminal import TERMINAL_HEIGHT, TERMINAL_WIDTH
from clive.__private.core.profile import Profile
from clive.__private.core.world import TUIWorld
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_pilot import ClivePilot
from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.help import Help
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.quit import Quit
from clive.__private.ui.screens.unlock import Unlock
from clive.exceptions import ScreenNotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Iterator

    from textual.message import Message
    from textual.screen import Screen, ScreenResultType
    from textual.worker import Worker


UpdateScreenResultT = TypeVar("UpdateScreenResultT")


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    from clive import __version__

    SUB_TITLE = __version__

    CSS_PATH = [get_relative_css_path(__file__, name="global")]

    AUTO_FOCUS = "*"

    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding("ctrl+s", "app.screenshot()", "Screenshot", show=False),
        Binding("ctrl+x", "push_screen('quit')", "Quit", show=False),
        Binding("c", "clear_notifications", "Clear notifications", show=False),
        Binding("f1", "help", "Help", show=False),
        Binding("f7", "go_to_transaction_summary", "Transaction summary", show=False),
        Binding("f8", "go_to_dashboard", "Dashboard", show=False),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard": Dashboard,
    }

    MODES = {
        "unlock": Unlock,
        "create_profile": CreateProfileForm,
        "dashboard": Dashboard,
    }

    header_expanded = var(default=False)
    """Synchronize the expanded header state in all created header objects."""

    notification_history: list[Notification] = var([], init=False)  # type: ignore[assignment]
    """A list of all notifications that were displayed."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._world: TUIWorld | None = None

    @property
    def world(self) -> TUIWorld:
        assert self._world is not None, "World is not set yet."
        return self._world

    @staticmethod
    def app_instance() -> Clive:
        return cast(Clive, active_app.get())

    @classmethod
    def is_launched(cls) -> bool:
        try:
            cls.app_instance()
        except LookupError:
            return False
        return True

    def notify(
        self,
        message: str,
        *,
        title: str = "",
        severity: SeverityLevel = "information",
        timeout: float | None = None,
    ) -> None:
        title = title if title else severity.capitalize()
        timeout = math.inf if timeout is None and severity == "error" else timeout
        logger.info(f"Sending notification: {severity=}, {title=}, {message=}")
        return super().notify(message, title=title, severity=severity, timeout=timeout)

    def is_notification_present(self, message: str) -> bool:
        current_notifications = self._notifications
        return any(notification.message == message for notification in current_notifications)

    @on(Notify)
    def _store_notification(self, event: Notify) -> None:
        self.notification_history.append(event.notification)
        self.mutate_reactive(self.__class__.notification_history)  # type: ignore[arg-type]

    @contextmanager
    def suppressed_notifications(self) -> Iterator[None]:
        """Suppress all notifications while in context."""

        def dummy_notify(*_: Any, **__: Any) -> None:
            pass

        old_notify = self.notify
        self.notify = dummy_notify  # type: ignore[method-assign]
        try:
            yield
        finally:
            self.notify = old_notify  # type: ignore[method-assign]

    @asynccontextmanager
    async def run_test(
        self,
        *,
        headless: bool = True,
        size: tuple[int, int] | None = (TERMINAL_WIDTH, TERMINAL_HEIGHT),
        tooltips: bool = False,
        notifications: bool = True,
        message_hook: Callable[[Message], None] | None = None,
    ) -> AsyncGenerator[ClivePilot]:
        async with super().run_test(
            headless=headless,
            size=size,
            tooltips=tooltips,
            notifications=notifications,
            message_hook=message_hook,
        ) as pilot:
            yield cast(ClivePilot, pilot)

    async def on_load(self) -> None:
        self.console.set_window_title("Clive")
        self._register_quit_signals()
        self._world = await TUIWorld().setup()

    def on_mount(self) -> None:
        self._refresh_node_data_interval = self.set_interval(
            safe_settings.node.refresh_rate_secs, lambda: self.update_data_from_node(), pause=True
        )
        self._refresh_alarms_data_interval = self.set_interval(
            safe_settings.node.refresh_alarms_rate_secs, lambda: self.update_alarms_data(), pause=True
        )

        self._refresh_beekeeper_wallet_lock_status_interval = self.set_interval(
            safe_settings.beekeeper.refresh_timeout_secs, self.update_wallet_lock_status_from_beekeeper
        )

        should_enable_debug_loop = safe_settings.dev.should_enable_debug_loop
        if should_enable_debug_loop:
            debug_loop_period_secs = safe_settings.dev.debug_loop_period_secs
            self.set_interval(debug_loop_period_secs, self.__debug_log)

        if Profile.is_any_profile_saved():
            self.switch_mode("unlock")
        else:
            self.switch_mode("create_profile")

    async def on_unmount(self) -> None:
        if self._world is not None:
            # There might be an exception during world setup and therefore world might not be available.
            # Then when accessing self.world, it will raise an exception which will hide the original one.
            await self._world.close()

    def get_screen_from_current_stack(self, screen: type[Screen[ScreenResultType]]) -> Screen[ScreenResultType]:
        for current_screen in self.screen_stack:
            if isinstance(current_screen, screen):
                return current_screen
        raise ScreenNotFoundError(f"Screen {screen} not found in stack")

    def action_help(self) -> None:
        if isinstance(self.screen, Help):
            return
        self.push_screen(Help())

    def action_clear_notifications(self) -> None:
        self.clear_notifications()

    def action_go_to_dashboard(self) -> None:
        self.get_screen_from_current_stack(Dashboard).pop_until_active()

    async def action_go_to_transaction_summary(self) -> None:
        from clive.__private.ui.screens.transaction_summary import TransactionSummary

        if isinstance(self.screen, TransactionSummary):
            return

        if not self.world.profile.transaction.is_signed:
            await self.world.commands.update_transaction_metadata(transaction=self.world.profile.transaction)
        await self.push_screen(TransactionSummary())

    def pause_refresh_alarms_data_interval(self) -> None:
        self._refresh_alarms_data_interval.pause()
        self.workers.cancel_group(self, "alarms_data")

    def resume_refresh_alarms_data_interval(self) -> None:
        self._refresh_alarms_data_interval.resume()

    def pause_refresh_node_data_interval(self) -> None:
        self._refresh_node_data_interval.pause()
        self.workers.cancel_group(self, "node_data")

    def resume_refresh_node_data_interval(self) -> None:
        self._refresh_node_data_interval.resume()

    def trigger_profile_watchers(self) -> None:
        asyncio_run(self.world.commands.save_profile())
        self.world.mutate_reactive(TUIWorld.profile_reactive)  # type: ignore[arg-type]

    def trigger_node_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.node_reactive)  # type: ignore[arg-type]

    def trigger_app_state_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.app_state)  # type: ignore[arg-type]

    def update_alarms_data_asap(self) -> Worker[None]:
        """Update alarms as soon as possible after node data becomes available."""

        async def _update_alarms_data_asap() -> None:
            self.pause_refresh_alarms_data_interval()
            while not self.world.profile.accounts.is_tracked_accounts_node_data_available:  # noqa: ASYNC110
                await asyncio.sleep(0.1)
            await self.update_alarms_data().wait()
            self.resume_refresh_alarms_data_interval()

        return self.run_worker(_update_alarms_data_asap())

    def update_data_from_node_asap(self) -> Worker[None]:
        async def _update_data_from_node_asap() -> None:
            self.pause_refresh_node_data_interval()
            await self.update_data_from_node().wait()
            self.resume_refresh_node_data_interval()

        return self.run_worker(_update_data_from_node_asap())

    def update_alarms_data_asap_on_newest_node_data(self) -> Worker[None]:
        """Update alarms on the newest possible node data."""

        async def _update_alarms_data_asap_on_newest_node_data() -> None:
            await self.update_data_from_node_asap().wait()
            await self.update_alarms_data_asap().wait()

        return self.run_worker(_update_alarms_data_asap_on_newest_node_data())

    @work(name="alarms data update worker", group="node_data")
    async def update_alarms_data(self) -> None:
        accounts = self.world.profile.accounts.tracked
        wrapper = await self.world.commands.update_alarms_data(accounts=accounts)
        if wrapper.error_occurred:
            logger.error(f"Update alarms data failed: {wrapper.error}")
            return

        self.trigger_profile_watchers()

    @work(name="node data update worker", group="alarms_data")
    async def update_data_from_node(self) -> None:
        accounts = self.world.profile.accounts.tracked  # accounts list gonna be empty, but dgpo will be refreshed

        wrapper = await self.world.commands.update_node_data(accounts=accounts)
        if wrapper.error_occurred:
            error = wrapper.error
            if isinstance(error, CommunicationError) and error.response is None:
                # notify watchers when node goes offline
                self.trigger_node_watchers()

            logger.error(f"Update node data failed: {wrapper.error}")
            return

        self.trigger_node_watchers()

    @work(name="beekeeper wallet lock status update worker")
    async def update_wallet_lock_status_from_beekeeper(self) -> None:
        if self.world._beekeeper_manager:
            await self.world.commands.sync_state_with_beekeeper("beekeeper_monitoring_thread")

    async def __debug_log(self) -> None:
        logger.debug("===================== DEBUG =====================")
        logger.debug(f"Currently focused: {self.focused}")
        logger.debug(f"Screen stack: {self.screen_stack}")

        response = await self.world.node.api.database.get_dynamic_global_properties()
        logger.debug(f"Current block: {response.head_block_number}")

        logger.debug("=================================================")

    def _handle_exception(self, error: Exception) -> None:
        # We already had a situation where Textual swallowed an exception without logging it.
        # This is a safeguard to prevent that from happening again.
        logger.error(f"{error.__class__.__name__}: {error}\n{traceback.format_exc()}")
        super()._handle_exception(error)

    def _register_quit_signals(self) -> None:
        import signal

        def callback() -> None:
            self.exit()

        loop = asyncio.get_running_loop()  # can't use self._loop since it's not set yet
        for signal_number in [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
            loop.add_signal_handler(signal_number, callback)
