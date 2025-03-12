from __future__ import annotations

import asyncio
import math
import traceback
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, Awaitable, ClassVar, TypeVar, cast, get_args

from beekeepy.exceptions import CommunicationError
from textual import on, work
from textual._context import active_app
from textual.app import App
from textual.await_complete import AwaitComplete
from textual.binding import Binding
from textual.notifications import Notification, Notify, SeverityLevel
from textual.reactive import var
from textual.worker import NoActiveWorker, WorkerCancelled, get_current_worker

from clive.__private.core.async_guard import AsyncGuard
from clive.__private.core.constants.terminal import TERMINAL_HEIGHT, TERMINAL_WIDTH
from clive.__private.core.constants.tui.bindings import APP_QUIT_KEY_BINDING
from clive.__private.core.profile import Profile
from clive.__private.core.world import TUIWorld
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_pilot import ClivePilot
from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.help import Help
from clive.__private.ui.screens.config import Config
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.quit import Quit
from clive.__private.ui.screens.unlock import Unlock
from clive.__private.ui.types import CliveModes
from clive.exceptions import ScreenNotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Iterator

    from textual.message import Message
    from textual.screen import Screen, ScreenResultType
    from textual.worker import Worker

    from clive.__private.core.app_state import LockSource
    from clive.__private.ui.clive_screen import CliveScreen

UpdateScreenResultT = TypeVar("UpdateScreenResultT")


class Clive(App[int]):
    """A singleton instance of the Clive app."""

    from clive import __version__

    SUB_TITLE = __version__

    CSS_PATH = [get_relative_css_path(__file__, name="global")]

    AUTO_FOCUS = "*"

    ENABLE_COMMAND_PALETTE = True
    COMMAND_PALETTE_BINDING = "f12"

    BINDINGS = [
        Binding("ctrl+s", "app.screenshot()", "Screenshot", show=False),
        Binding(APP_QUIT_KEY_BINDING, "quit", "Quit", show=False),
        Binding("c", "clear_notifications", "Clear notifications", show=False),
        Binding("f1", "help", "Help", show=False),
        Binding("f7", "go_to_transaction_summary", "Transaction summary", show=False),
        Binding("f8", "go_to_dashboard", "Dashboard", show=False),
        Binding("f9", "go_to_config", "Config", show=False),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard": Dashboard,
    }

    MODES: ClassVar[dict[CliveModes, type[CliveScreen]]] = {  # type: ignore[assignment]
        "unlock": Unlock,
        "create_profile": CreateProfileForm,
        "dashboard": Dashboard,
        "config": Config,
    }

    header_expanded = var(default=False)
    """Synchronize the expanded header state in all created header objects."""

    notification_history: list[Notification] = var([], init=False)  # type: ignore[assignment]
    """A list of all notifications that were displayed."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._world: TUIWorld | None = None

        self._screen_remove_guard = AsyncGuard()
        """
        Due to https://github.com/Textualize/textual/issues/5008.

        Any action that involves removing a screen like remove_mode/switch_screen/pop_screen
        cannot be awaited in the @on handler like Button.Pressed because it will deadlock the app.
        Workaround is to not await mentioned action or run it in a separate task if something later needs to await it.
        This workaround can create race conditions, so we need to guard against it.
        """

    @property
    def world(self) -> TUIWorld:
        assert self._world is not None, "World is not set yet."
        return self._world

    @property
    def current_mode(self) -> CliveModes:
        mode = super().current_mode
        modes = get_args(CliveModes)
        assert mode in modes, f"Mode {mode} is not in the list of modes: {modes}"
        return cast("CliveModes", mode)

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

    async def on_mount(self) -> None:
        self._refresh_node_data_interval = self.set_interval(
            safe_settings.node.refresh_rate_secs, self._retrigger_update_data_from_node, pause=True
        )
        self._refresh_alarms_data_interval = self.set_interval(
            safe_settings.node.refresh_alarms_rate_secs, self._retrigger_update_alarms_data, pause=True
        )

        self._refresh_beekeeper_wallet_lock_status_interval = self.set_interval(
            safe_settings.beekeeper.refresh_timeout_secs,
            self._retrigger_update_wallet_lock_status_from_beekeeper,
            pause=True,
        )
        self.watch(self.world, "profile_reactive", self.save_profile_in_worker)

        should_enable_debug_loop = safe_settings.dev.should_enable_debug_loop
        if should_enable_debug_loop:
            debug_loop_period_secs = safe_settings.dev.debug_loop_period_secs
            self.set_interval(debug_loop_period_secs, self._debug_log)

        await self._switch_to_initial_mode()

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

    async def action_quit(self) -> None:
        self.push_screen(Quit())

    def action_help(self) -> None:
        if isinstance(self.screen, Help):
            return
        self.push_screen(Help())

    def action_clear_notifications(self) -> None:
        self.clear_notifications()

    async def action_go_to_config(self) -> None:
        with self._screen_remove_guard.suppress(), self._screen_remove_guard.guard():
            await self.go_to_config()

    async def action_go_to_dashboard(self) -> None:
        with self._screen_remove_guard.suppress(), self._screen_remove_guard.guard():
            await self.go_to_dashboard()

    async def action_go_to_transaction_summary(self) -> None:
        with self._screen_remove_guard.suppress(), self._screen_remove_guard.guard():
            await self.go_to_transaction_summary()

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

    def pause_refresh_beekeeper_wallet_lock_status_interval(self) -> None:
        self._refresh_beekeeper_wallet_lock_status_interval.pause()
        self.workers.cancel_group(self, "wallet_lock_status")

    def resume_refresh_beekeeper_wallet_lock_status_interval(self) -> None:
        self._refresh_beekeeper_wallet_lock_status_interval.resume()

    def pause_periodic_intervals(self) -> None:
        self.pause_refresh_node_data_interval()
        self.pause_refresh_alarms_data_interval()
        self.pause_refresh_beekeeper_wallet_lock_status_interval()

    def resume_periodic_intervals(self) -> None:
        self.resume_refresh_node_data_interval()
        self.resume_refresh_alarms_data_interval()
        self.resume_refresh_beekeeper_wallet_lock_status_interval()

    def trigger_profile_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.profile_reactive)  # type: ignore[arg-type]

    def trigger_node_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.node_reactive)  # type: ignore[arg-type]

    def trigger_app_state_watchers(self) -> None:
        self.world.mutate_reactive(TUIWorld.app_state)  # type: ignore[arg-type]

    def update_alarms_data_on_newest_node_data(self, *, suppress_cancelled_error: bool = False) -> Worker[None]:
        """There is periodic work refreshing alarms data and node data, this method triggers immediate update."""

        async def _update_alarms_data_on_newest_node_data() -> None:
            try:
                await self.update_data_from_node().wait()
                await self.update_alarms_data().wait()
            except WorkerCancelled as error:
                logger.warning("Update alarms data on newest node data cancelled.")
                if not suppress_cancelled_error:
                    logger.warning(f"Re-raising exception: {error}")
                    raise
                logger.warning(f"Ignoring exception: {error}")

        return self.run_worker(_update_alarms_data_on_newest_node_data(), exclusive=True)

    @work(name="alarms data update worker", group="alarms_data", exclusive=True)
    async def update_alarms_data(self) -> None:
        while not self.world.profile.accounts.is_tracked_accounts_node_data_available:  # noqa: ASYNC110
            await asyncio.sleep(0.1)
        accounts = self.world.profile.accounts.tracked
        wrapper = await self.world.commands.update_alarms_data(accounts=accounts)
        if wrapper.error_occurred:
            logger.error(f"Update alarms data failed: {wrapper.error}")
            return

        self.trigger_profile_watchers()

    @work(name="node data update worker", group="node_data", exclusive=True)
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

        self.trigger_profile_watchers()
        self.trigger_node_watchers()

    @work(name="beekeeper wallet lock status update worker", group="wallet_lock_status")
    async def update_wallet_lock_status_from_beekeeper(self) -> None:
        await self.world.commands.sync_state_with_beekeeper("beekeeper_wallet_lock_status_update_worker")

    def switch_mode_with_reset(self, new_mode: CliveModes) -> AwaitComplete:
        """
        Switch mode and reset all other active modes.

        The `App.switch_mode` method from Textual keeps the previous mode in the stack.
        This method allows to switch to a new mode and have only a new mode in the stack without keeping
        any other screen stacks.

        Args:
        ----
            new_mode: The mode to switch to.
        """

        async def impl() -> None:
            logger.debug(f"Switching mode from: `{self.current_mode}` to: `{new_mode}`")
            await self.switch_mode(new_mode)

            modes_to_keep = (new_mode, "_default")
            modes_to_reset = [mode for mode in self._screen_stacks if mode not in modes_to_keep]
            assert all(mode in self.MODES for mode in modes_to_reset), "Unexpected mode in modes_to_reset"
            await self.reset_mode(*cast("list[CliveModes]", modes_to_reset))

        return AwaitComplete(impl()).call_next(self)

    def reset_mode(self, *modes: CliveModes) -> AwaitComplete:
        async def impl() -> None:
            logger.debug(f"Resetting modes: {modes}")
            for mode in modes:
                await self.remove_mode(mode)
                self.add_mode(mode, self.MODES[mode])

        return AwaitComplete(impl()).call_next(self)

    async def switch_mode_into_locked(self, *, save_profile: bool = True) -> None:
        if save_profile:
            await self.world.commands.save_profile()

        # needs to be done before beekeeper API call to avoid race condition between manual lock and timeout lock
        self.pause_refresh_beekeeper_wallet_lock_status_interval()

        await self.world.commands.lock()

    async def go_to_config(self) -> None:
        if self.current_mode == "config":
            self.get_screen_from_current_stack(Config).pop_until_active()
        elif self.current_mode == "dashboard":
            await self.switch_mode_with_reset("config")
        else:
            raise AssertionError(f"Unexpected mode: {self.current_mode}")

    async def go_to_dashboard(self) -> None:
        if self.current_mode == "dashboard":
            self.get_screen_from_current_stack(Dashboard).pop_until_active()
        elif self.current_mode == "config":
            await self.switch_mode_with_reset("dashboard")
        else:
            raise AssertionError(f"Unexpected mode: {self.current_mode}")

    async def go_to_transaction_summary(self) -> None:
        from clive.__private.ui.screens.transaction_summary import TransactionSummary

        if isinstance(self.screen, TransactionSummary):
            return

        if self.current_mode == "config":
            await self.switch_mode_with_reset("dashboard")

        if not self.world.profile.transaction.is_signed:
            await self.world.commands.update_transaction_metadata(transaction=self.world.profile.transaction)
        await self.push_screen(TransactionSummary())

    def run_worker_with_guard(self, awaitable: Awaitable[None], guard: AsyncGuard) -> None:
        """Run work in a worker with a guard. It means that the work will be executed only if the guard is available."""

        async def work_with_release() -> None:
            try:
                await awaitable
            finally:
                guard.release()

        with guard.suppress():
            guard.acquire()
            self.run_worker(work_with_release())

    def run_worker_with_screen_remove_guard(self, awaitable: Awaitable[None]) -> None:
        self.run_worker_with_guard(awaitable, self._screen_remove_guard)

    def save_profile_in_worker(self, profile: Profile | None) -> None:
        async def impl() -> None:
            if profile is not None:
                await self.world.commands.save_profile()

        self.app.run_worker(impl(), name="save profile worker", group="save_profile", exclusive=True)

    async def _debug_log(self) -> None:
        logger.debug("===================== DEBUG =====================")
        logger.debug(f"Currently focused: {self.focused}")
        logger.debug(f"Current mode: {self.current_mode}")
        logger.debug(f"Screen stack: {self.screen_stack}")
        logger.debug(f"Screen stacks: {self._screen_stacks}")

        if self.world.is_node_available:
            cached_dgpo = self.world.node.cached.dynamic_global_properties_or_none
            message = (
                f"Currently cached head block number: {cached_dgpo.head_block_number}"
                if cached_dgpo
                else "Node cache seems to be empty, no head block number available."
            )
            logger.debug(message)

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

    def is_worker_group_empty(self, group: str) -> bool:
        return not bool([worker for worker in self.workers if worker.group == group])

    def _retrigger_update_data_from_node(self) -> None:
        if self.is_worker_group_empty("node_data"):
            self.update_data_from_node()

    def _retrigger_update_alarms_data(self) -> None:
        if self.is_worker_group_empty("alarms_data"):
            self.update_alarms_data()

    def _retrigger_update_wallet_lock_status_from_beekeeper(self) -> None:
        if self.is_worker_group_empty("wallet_lock_status"):
            self.update_wallet_lock_status_from_beekeeper()

    async def _switch_to_initial_mode(self) -> None:
        if not Profile.is_any_profile_saved():
            await self.switch_mode("create_profile")
            return

        if self.world.app_state.is_unlocked:
            await self._switch_mode_into_unlocked()
        else:
            await self._switch_mode_into_locked()

    async def _switch_mode_into_locked(self, source: LockSource = "unknown") -> None:
        if source == "beekeeper_wallet_lock_status_update_worker":
            self.notify("Switched to the LOCKED mode due to timeout.", timeout=10)

        self.pause_periodic_intervals()

        # There might be ongoing workers that should be cancelled (e.g. DynamicWidget update)
        self._cancel_workers_except_current()

        if self.world.is_node_available:
            self.world.node.cached.clear()

        await self.switch_mode_with_reset("unlock")
        await self.world.switch_profile(None)

    async def _switch_mode_into_unlocked(self) -> None:
        await self.switch_mode_with_reset("dashboard")
        self.update_alarms_data_on_newest_node_data(suppress_cancelled_error=True)
        self.resume_periodic_intervals()

    def _cancel_workers_except_current(self) -> None:
        try:
            current_worker = get_current_worker()
        except NoActiveWorker:
            current_worker = None

        for worker in self.workers:
            if worker != current_worker:
                worker.cancel()
