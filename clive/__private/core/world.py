from __future__ import annotations

import contextlib
from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING, Any, Final, Generator, cast

from textual.reactive import var

from clive.__private.core.app_state import AppState, LockSource
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.commands import CLICommands, Commands, TUICommands
from clive.__private.core.communication import Communication
from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.known_exchanges import KnownExchanges
from clive.__private.core.node.node import Node
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_dom_node import CliveDOMNode
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.screens.unlock import Unlock

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType
    from typing import Literal

    from typing_extensions import Self

    from clive.__private.core.url import Url


class World:
    """
    World is a top-level container for all application objects.

    It is a single source of truth for interacting with the Clive application.

    Args:
    ----
    profile_name: Name of the profile to load. If None is passed, the default profile is loaded.
    use_beekeeper: If True, there will be access to beekeeper. If False, beekeeper will not be available.
    beekeeper_remote_endpoint: If given, remote beekeeper will be used. If not given, local beekeeper will start.
    """

    def __init__(
        self,
        profile_name: str | None = None,
        beekeeper_remote_endpoint: Url | None = None,
        *args: Any,
        use_beekeeper: bool = True,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._profile = self._load_profile(profile_name)
        self._known_exchanges = KnownExchanges()
        self._app_state = AppState(self)
        self._commands = self._setup_commands()

        self._use_beekeeper = use_beekeeper
        self._beekeeper_remote_endpoint = beekeeper_remote_endpoint
        self._beekeeper: Beekeeper | None = None

        self._node = Node(self._profile)
        self._is_during_setup = False

    async def __aenter__(self) -> Self:
        return await self.setup()

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    @property
    def commands(self) -> Commands[World]:
        return self._commands

    @property
    def known_exchanges(self) -> KnownExchanges:
        return self._known_exchanges

    @property
    def beekeeper(self) -> Beekeeper:
        assert self._beekeeper is not None, "Beekeeper is not initialized"
        return self._beekeeper

    @property
    def node(self) -> Node:
        return self._node

    @property
    def _should_sync_with_beekeeper(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = Communication.DEFAULT_ATTEMPTS,
        timeout_total_secs: float = Communication.DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = Communication.DEFAULT_POOL_TIME_SECONDS,
        target: Literal["beekeeper", "node", "all"] = "all",
    ) -> Iterator[None]:
        """Temporarily change connection details."""
        contexts_to_enter = []
        if target in ("beekeeper", "all"):
            contexts_to_enter.append(
                self.beekeeper.modified_connection_details(max_attempts, timeout_total_secs, pool_time_secs)
            )
        if target in ("node", "all"):
            contexts_to_enter.append(
                self.node.modified_connection_details(max_attempts, timeout_total_secs, pool_time_secs)
            )

        with contextlib.ExitStack() as stack:
            for context in contexts_to_enter:
                stack.enter_context(context)
            yield

    @contextmanager
    def during_setup(self) -> Generator[None, None]:
        self._is_during_setup = True
        try:
            yield
        finally:
            self._is_during_setup = False

    async def setup(self) -> Self:
        with self.during_setup():
            await self._node.setup()
            if self._use_beekeeper:
                self._beekeeper = await self.__setup_beekeeper(remote_endpoint=self._beekeeper_remote_endpoint)
                if self._should_sync_with_beekeeper:
                    await self._commands.sync_state_with_beekeeper()
        return self

    async def close(self) -> None:
        self.profile.save()
        await self._node.teardown()
        if self._beekeeper is not None:
            await self._beekeeper.close()

    def on_going_into_locked_mode(self, source: LockSource) -> None:
        """Triggered when the application is going into the locked mode."""
        if self._is_during_setup:
            return
        self._on_going_into_locked_mode(source)

    def on_going_into_unlocked_mode(self) -> None:
        """Triggered when the application is going into the unlocked mode."""
        if self._is_during_setup:
            return
        self._on_going_into_unlocked_mode()

    def _on_going_into_locked_mode(self, _: LockSource) -> None:
        """Override this method to hook when clive goes into the locked mode."""

    def _on_going_into_unlocked_mode(self) -> None:
        """Override this method to hook when clive goes into the unlocked mode."""

    def _load_profile(self, profile_name: str | None) -> Profile:
        return Profile.load(profile_name)

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

    async def __setup_beekeeper(self, *, remote_endpoint: Url | None = None) -> Beekeeper:
        beekeeper = Beekeeper(
            remote_endpoint=remote_endpoint,
            notify_closing_wallet_name_cb=lambda: self.profile.name,
        )
        beekeeper.attach_wallet_closing_listener(self.app_state)
        await beekeeper.launch()
        return beekeeper

    @property
    def profile(self) -> Profile:
        return self._profile

    @property
    def app_state(self) -> AppState:
        return self._app_state


class TUIWorld(World, CliveDOMNode):
    profile: Profile = var(None, init=False)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]
    node: Node = var(None)  # type: ignore[assignment]

    def __init__(self) -> None:
        profile_name = WELCOME_PROFILE_NAME
        super().__init__(profile_name)
        self.node = self._node
        self.profile = self._profile
        self.app_state = self._app_state

    def _load_profile(self, profile_name: str | None) -> Profile:
        profile = super()._load_profile(profile_name)
        if self._is_in_onboarding_mode(profile):
            profile.skip_saving()
        return profile

    @property
    def commands(self) -> TUICommands:
        return cast(TUICommands, super().commands)

    @property
    def is_in_onboarding_mode(self) -> bool:
        return self._is_in_onboarding_mode(self.profile)

    def _switch_to_welcome_profile(self) -> None:
        """Set the profile to default (welcome)."""
        self.profile = self._load_profile(WELCOME_PROFILE_NAME)

    def _watch_profile(self, profile: Profile) -> None:
        self.node.change_related_profile(profile)

    def _on_going_into_locked_mode(self, source: LockSource) -> None:
        base_message: Final[str] = "Switched to the LOCKED mode"
        if source == "beekeeper_notification_server":
            send_notification = partial(
                self.app.notify,
                f"{base_message} due to inactivity in a temporary unlock mode.",
                timeout=10,
            )
        else:
            send_notification = partial(self.app.notify, f"{base_message}.")

        self.profile.save()

        async def lock() -> None:
            nonlocal send_notification

            self._add_welcome_modes()
            await self.app.switch_mode("unlock")
            await self._restart_dashboard_mode()
            self._switch_to_welcome_profile()
            send_notification()

        self.app.run_worker(lock())

    def _on_going_into_unlocked_mode(self) -> None:
        self.app.notify("Switched to the UNLOCKED mode.")
        self.app.trigger_app_state_watchers()

    @property
    def _should_sync_with_beekeeper(self) -> bool:
        return super()._should_sync_with_beekeeper and not self.is_in_onboarding_mode

    def _is_in_onboarding_mode(self, profile: Profile) -> bool:
        return profile.name == WELCOME_PROFILE_NAME

    def _setup_commands(self) -> TUICommands:
        return TUICommands(self)

    def _add_welcome_modes(self) -> None:
        self.app.add_mode("onboarding", Onboarding)
        self.app.add_mode("unlock", Unlock)

    async def _restart_dashboard_mode(self) -> None:
        await self.app.remove_mode("dashboard")
        self.app.add_mode("dashboard", Dashboard)


class CLIWorld(World):
    @property
    def commands(self) -> CLICommands:
        return cast(CLICommands, super().commands)

    def _setup_commands(self) -> CLICommands:
        return CLICommands(self)

    def _load_profile(self, profile_name: str | None) -> Profile:
        return Profile.load(profile_name, auto_create=False)
