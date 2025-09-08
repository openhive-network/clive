from __future__ import annotations

import asyncio
import math
import traceback
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, ClassVar, Final, cast, get_args

import beekeepy.exceptions as bke
from textual import on, work
from textual._context import active_app
from textual.app import App
from textual.await_complete import AwaitComplete
from textual.notifications import Notification, Notify, SeverityLevel
from textual.reactive import var
from textual.worker import NoActiveWorker, WorkerCancelled, get_current_worker

from clive.__private.core.async_guard import AsyncGuard
from clive.__private.core.constants.terminal import TERMINAL_HEIGHT, TERMINAL_WIDTH
from clive.__private.core.constants.tui.themes import DEFAULT_THEME
from clive.__private.core.profile import Profile
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS, BindingFileInvalidError, load_custom_bindings
from clive.__private.ui.clive_pilot import ClivePilot
from clive.__private.ui.dialogs import LoadTransactionFromFileDialog
from clive.__private.ui.dialogs.switch_node_address_dialog import SwitchNodeAddressDialog
from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm
from clive.__private.ui.forms.create_profile.profile_credentials_form_screen import ProfileCredentialsFormScreen
from clive.__private.ui.forms.create_profile.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.help import Help
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.quit import Quit
from clive.__private.ui.screens.settings import Settings
from clive.__private.ui.screens.settings.switch_node_address import SwitchNodeAddress
from clive.__private.ui.screens.transaction_summary import TransactionSummary
from clive.__private.ui.screens.unlock import Unlock
from clive.__private.ui.tui_world import TUIWorld
from clive.__private.ui.types import CliveModes
from clive.exceptions import ScreenNotFoundError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable, Iterator

    from textual.message import Message
    from textual.screen import Screen, ScreenResultType
    from textual.worker import Worker

    from clive.__private.core.app_state import LockSource
    from clive.__private.ui.bindings import CliveBindings
    from clive.__private.ui.clive_pilot import ClivePilot
    from clive.__private.ui.clive_screen import CliveScreen


class Clive(App[int]):
    """
    A singleton instance of the Clive app.

    Attributes:
        SUB_TITLE: The version of the Clive app.
        CSS_PATH: The path to the global CSS file.
        ENABLE_COMMAND_PALETTE: Whether the command palette is enabled.
        COMMAND_PALETTE_BINDING: The key binding to open the command palette.
        BINDINGS: Key bindings for the app.
        SCREENS: Screens available in the app.
        MODES: Modes available in the app.
        header_expanded: Synchronize the expanded header state in all created header objects.
        is_help_panel_visible: Synchronize the help panel presence state across all screens.
        notification_history: All notifications that were displayed.

    Args:
        *args: Positional arguments for the App class.
        **kwargs: Keyword arguments for the App class.
    """

    from clive import __version__  # noqa: PLC0415

    SUB_TITLE = __version__

    CSS_PATH = [get_relative_css_path(__file__, name="global")]

    ENABLE_COMMAND_PALETTE = True
    COMMAND_PALETTE_BINDING = "ctrl+p"

    BINDINGS = [
        CLIVE_PREDEFINED_BINDINGS.help.toggle_help.create(action="help", description="Help", show=False),
        CLIVE_PREDEFINED_BINDINGS.app.clear_notifications.create(show=False),
        CLIVE_PREDEFINED_BINDINGS.app.load_transaction_from_file.create(show=False),
        CLIVE_PREDEFINED_BINDINGS.app.quit.create(show=False),
        CLIVE_PREDEFINED_BINDINGS.app.switch_node.create(show=False),
        CLIVE_PREDEFINED_BINDINGS.app.toggle_keys_panel.create(show=False),
        CLIVE_PREDEFINED_BINDINGS.app.dashboard.create(),
        CLIVE_PREDEFINED_BINDINGS.app.lock_wallet.create(),
        CLIVE_PREDEFINED_BINDINGS.app.settings.create(),
        CLIVE_PREDEFINED_BINDINGS.app.transaction_summary.create(),
    ]

    SCREENS = {
        "quit": Quit,
        "dashboard": Dashboard,
    }

    MODES: ClassVar[dict[CliveModes, type[CliveScreen]]] = {  # type: ignore[assignment]
        "unlock": Unlock,
        "create_profile": CreateProfileForm,
        "dashboard": Dashboard,
        "settings": Settings,
    }

    _WALLET_LOCK_STATUS_WORKER_GROUP_NAME: Final[str] = "wallet_lock_status"
    _NODE_DATA_WORKER_GROUP_NAME: Final[str] = "node_data"
    _ALARMS_DATA_WORKER_GROUP_NAME: Final[str] = "alarms_data"

    header_expanded = var(default=False)
    is_help_panel_visible = var(default=False, init=False)
    """Used to synchronize the help panel presence state across all screens."""

    notification_history: list[Notification] = var([], init=False)  # type: ignore[assignment]

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
        self.custom_bindings = self._load_bindings_from_file()
        self.update_keymap(self.custom_bindings.keymap)

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
        return cast("Clive", active_app.get())

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:  # noqa: ARG002
        """Check whether an action is enabled/visible.

        Args:
            action: The name of an action.
            parameters: A tuple of any action parameters.

        Returns:
            `True` if the action is enabled+visible,
            `False` if the action is disabled+hidden,
            `None` if the action is disabled+visible (grayed out in footer)
        """
        app_section = self.custom_bindings.app

        actions_hidden_when_not_unlocked = [
            app_section.load_transaction_from_file.default_action,
            app_section.dashboard.default_action,
            app_section.lock_wallet.default_action,
            app_section.settings.default_action,
            app_section.transaction_summary.default_action,
        ]

        mode_to_hidden_actions: dict[CliveModes, list[str]] = {
            "unlock": actions_hidden_when_not_unlocked,
            "create_profile": actions_hidden_when_not_unlocked,
        }

        screen_to_hidden_actions: dict[type[CliveScreen], list[str]] = {
            Dashboard: [app_section.dashboard.default_action],
            Settings: [app_section.settings.default_action],
            TransactionSummary: [app_section.transaction_summary.default_action],
            Unlock: [app_section.switch_node.default_action],
            WelcomeFormScreen: [app_section.switch_node.default_action],
            ProfileCredentialsFormScreen: [app_section.switch_node.default_action],
        }

        if action in mode_to_hidden_actions.get(self.current_mode, []):
            return False

        for screen_type, actions in screen_to_hidden_actions.items():
            if isinstance(self.screen, screen_type) and action in actions:
                return False

        return True

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
        markup: bool = True,
    ) -> None:
        title = title if title else severity.capitalize()
        timeout = math.inf if timeout is None and severity == "error" else timeout
        logger.info(f"Sending notification: {severity=}, {title=}, {message=}")
        return super().notify(message, title=title, severity=severity, timeout=timeout, markup=markup)

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
            yield cast("ClivePilot", pilot)

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
        self.watch(self, "theme", self._update_theme_in_profile)

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

    async def action_settings(self) -> None:
        with self._screen_remove_guard.suppress(), self._screen_remove_guard.guard():
            await self.go_to_settings()

    async def action_dashboard(self) -> None:
        with self._screen_remove_guard.suppress(), self._screen_remove_guard.guard():
            await self.go_to_dashboard()

    def action_load_transaction_from_file(self) -> None:
        if not self.world.app_state.is_unlocked:
            return
        self.push_screen(LoadTransactionFromFileDialog())

    def action_show_help_panel(self) -> None:
        """Adds support for global state of help panel."""
        self.is_help_panel_visible = True

    def action_hide_help_panel(self) -> None:
        """Adds support for global state of help panel."""
        self.is_help_panel_visible = False

    def action_toggle_keys_panel(self) -> None:
        self.is_help_panel_visible = not self.is_help_panel_visible

    async def action_transaction_summary(self) -> None:
        with self._screen_remove_guard.suppress(), self._screen_remove_guard.guard():
            await self.go_to_transaction_summary()

    async def action_lock_wallet(self) -> None:
        with self._screen_remove_guard.suppress(), self._screen_remove_guard.guard():
            await self.switch_mode_into_locked()

    async def action_switch_node(self) -> None:
        self.show_switch_node_address_dialog()

    def show_switch_node_address_dialog(self) -> None:
        if self.current_mode == "unlock":
            return
        if isinstance(self.screen, SwitchNodeAddressDialog | SwitchNodeAddress):
            return
        self.push_screen(SwitchNodeAddressDialog())

    def pause_refresh_alarms_data_interval(self) -> None:
        self._refresh_alarms_data_interval.pause()
        self.workers.cancel_group(self, self._ALARMS_DATA_WORKER_GROUP_NAME)

    def resume_refresh_alarms_data_interval(self) -> None:
        self._refresh_alarms_data_interval.resume()

    def pause_refresh_node_data_interval(self) -> None:
        self._refresh_node_data_interval.pause()
        self.workers.cancel_group(self, self._NODE_DATA_WORKER_GROUP_NAME)

    def resume_refresh_node_data_interval(self) -> None:
        self._refresh_node_data_interval.resume()

    async def pause_refresh_beekeeper_wallet_lock_status_interval(self) -> None:
        self._refresh_beekeeper_wallet_lock_status_interval.pause()
        await self._wait_for_worker_group_except_current(self._WALLET_LOCK_STATUS_WORKER_GROUP_NAME)

    def resume_refresh_beekeeper_wallet_lock_status_interval(self) -> None:
        self._refresh_beekeeper_wallet_lock_status_interval.resume()

    async def pause_periodic_intervals(self) -> None:
        self.pause_refresh_node_data_interval()
        self.pause_refresh_alarms_data_interval()
        await self.pause_refresh_beekeeper_wallet_lock_status_interval()

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
        """
        There is periodic work refreshing alarms data and node data, this method triggers immediate update.

        Args:
            suppress_cancelled_error: If True, suppresses WorkerCancelled exceptions.

        Returns:
            A worker that runs the update_alarms_data method after the update_data_from_node method.
        """

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

    @work(name="alarms data update worker", group=_ALARMS_DATA_WORKER_GROUP_NAME, exclusive=True)
    async def update_alarms_data(self) -> None:
        while not self.world.profile.accounts.is_tracked_accounts_node_data_available:  # noqa: ASYNC110
            await asyncio.sleep(0.1)
        accounts = self.world.profile.accounts.tracked
        wrapper = await self.world.commands.update_alarms_data(accounts=accounts)
        if wrapper.error_occurred:
            logger.error(f"Update alarms data failed: {wrapper.error}")
            return

        self.trigger_profile_watchers()

    @work(name="node data update worker", group=_NODE_DATA_WORKER_GROUP_NAME, exclusive=True)
    async def update_data_from_node(self) -> None:
        accounts = self.world.profile.accounts.tracked  # accounts list gonna be empty, but dgpo will be refreshed

        wrapper = await self.world.commands.update_node_data(accounts=accounts)
        if wrapper.error_occurred:
            error = wrapper.error
            if isinstance(error, bke.CommunicationError) and error.response is None:
                # notify watchers when node goes offline
                self.trigger_node_watchers()

            logger.error(f"Update node data failed: {wrapper.error}")
            return

        self.trigger_profile_watchers()
        self.trigger_node_watchers()

    @work(name="beekeeper wallet lock status update worker", group=_WALLET_LOCK_STATUS_WORKER_GROUP_NAME)
    async def update_wallet_lock_status_from_beekeeper(self) -> None:
        await self.world.commands.sync_state_with_beekeeper("beekeeper_wallet_lock_status_update_worker")

    def switch_mode_with_reset(self, new_mode: CliveModes) -> AwaitComplete:
        """
        Switch mode and reset all other active modes.

        The `App.switch_mode` method from Textual keeps the previous mode in the stack.
        This method allows to switch to a new mode and have only a new mode in the stack without keeping
        any other screen stacks.

        Args:
            new_mode: The mode to switch to.

        Returns:
            An awaitable that completes when the mode is switched.
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
        if not self.world.app_state.is_unlocked:
            return

        if save_profile:
            await self.world.commands.save_profile()

        # needs to be done before beekeeper API call to avoid race condition between manual lock and timeout lock
        await self.pause_refresh_beekeeper_wallet_lock_status_interval()

        await self.world.commands.lock()

    async def go_to_settings(self) -> None:
        if not self.world.app_state.is_unlocked:
            return
        if self.current_mode == "settings":
            self.get_screen_from_current_stack(Settings).pop_until_active()
        elif self.current_mode == "dashboard":
            await self.switch_mode_with_reset("settings")
        else:
            raise AssertionError(f"Unexpected mode: {self.current_mode}")

    async def go_to_dashboard(self) -> None:
        if not self.world.app_state.is_unlocked:
            return
        if self.current_mode == "dashboard":
            self.get_screen_from_current_stack(Dashboard).pop_until_active()
        elif self.current_mode == "settings":
            await self.switch_mode_with_reset("dashboard")
        else:
            raise AssertionError(f"Unexpected mode: {self.current_mode}")

    async def go_to_transaction_summary(self) -> None:
        from clive.__private.ui.screens.transaction_summary import TransactionSummary  # noqa: PLC0415

        if not self.world.app_state.is_unlocked:
            return

        if isinstance(self.screen, TransactionSummary):
            return

        if self.current_mode == "settings":
            await self.switch_mode_with_reset("dashboard")

        if not self.world.profile.transaction.is_signed:
            await self.world.commands.update_transaction_metadata(transaction=self.world.profile.transaction)
        await self.push_screen(TransactionSummary())

    def run_worker_with_guard(self, awaitable: Awaitable[None], guard: AsyncGuard) -> None:
        """
        Run work in a worker with a guard. It means that the work will be executed only if the guard is available.

        Args:
            awaitable: Represents the work to be done.
            guard: Will be used to control access to the work.
        """

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

    def _watch_is_help_panel_visible(self, is_help_panel_visible: bool) -> None:  # noqa: FBT001
        """
        Synchronize the presence of help panel on all the existing screens.

        Since help panel is a separate widget for every screen, we need to handle its presence manually.

        Args:
            is_help_panel_visible: New value of reactive responsible for global state of help panel presence.
        """
        for screen_ in self.screen_stack:
            screen = cast("CliveScreen", screen_)
            screen.toggle_help_panel(show=is_help_panel_visible)

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
        import signal  # noqa: PLC0415

        def callback() -> None:
            self.exit()

        loop = asyncio.get_running_loop()  # can't use self._loop since it's not set yet
        for signal_number in [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
            loop.add_signal_handler(signal_number, callback)

    def is_worker_group_empty(self, group: str) -> bool:
        return not bool([worker for worker in self.workers if worker.group == group])

    def _retrigger_update_data_from_node(self) -> None:
        if self.is_worker_group_empty(self._NODE_DATA_WORKER_GROUP_NAME):
            self.update_data_from_node()

    def _retrigger_update_alarms_data(self) -> None:
        if self.is_worker_group_empty(self._ALARMS_DATA_WORKER_GROUP_NAME):
            self.update_alarms_data()

    def _retrigger_update_wallet_lock_status_from_beekeeper(self) -> None:
        if self.is_worker_group_empty(self._WALLET_LOCK_STATUS_WORKER_GROUP_NAME):
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

        await self.pause_periodic_intervals()
        self.theme = DEFAULT_THEME

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
        self.theme = self.world.profile.tui_theme

    def _load_bindings_from_file(self) -> CliveBindings:
        """If there is exception and bindings cannot be loaded, notification is pushed."""
        try:
            custom_bindings = load_custom_bindings()
        except BindingFileInvalidError as error:
            message = f"Failed to load bindings: {error}. Using default bindings instead."
            self.notify(message, severity="error")
            custom_bindings = CLIVE_PREDEFINED_BINDINGS
        return custom_bindings

    def _get_current_worker(self) -> Worker[Any] | None:
        try:
            return get_current_worker()
        except NoActiveWorker:
            return None

    def _cancel_workers_except_current(self) -> None:
        current_worker = self._get_current_worker()

        for worker in self.workers:
            if worker != current_worker:
                worker.cancel()

    async def _wait_for_worker_group_except_current(self, group_name: str) -> None:
        for worker in self.workers:
            if worker.group == group_name and self._get_current_worker() != worker:
                await worker.wait()

    def _update_theme_in_profile(self, theme: str) -> None:
        if self.world.is_profile_available:
            self.world.profile.tui_theme = theme
