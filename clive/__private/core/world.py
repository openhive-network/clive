from __future__ import annotations

import contextlib
from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING, Any, Final, cast

from textual.reactive import var

from clive.__private.core.app_state import AppState, LockSource
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.beekeeper.exceptions import BeekeeperNotUnlockedError
from clive.__private.core.commands.commands import CLICommands, Commands, TUICommands
from clive.__private.core.communication import Communication
from clive.__private.core.known_exchanges import KnownExchanges
from clive.__private.core.node.node import Node
from clive.__private.core.profile import Profile
from clive.__private.storage.service import PersistentStorageService, ProfileDoesNotExistsError
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.exceptions import ScreenNotFoundError

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
    beekeeper_remote_endpoint: If given, remote beekeeper will be used. If not given, local beekeeper will start.
    """

    def __init__(
        self,
        beekeeper_remote_endpoint: Url | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)
        self._beekeeper_remote_endpoint = beekeeper_remote_endpoint

        self._known_exchanges = KnownExchanges()
        self._app_state = AppState(self)
        self._commands = self._setup_commands()

        self._beekeeper: Beekeeper | None = None
        self._persistent_storage_service: PersistentStorageService | None = None
        self._profile: Profile | None = None
        self._node: Node | None = None

    async def __aenter__(self) -> Self:
        return await self.setup()

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.close()

    @property
    def app_state(self) -> AppState:
        return self._app_state

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
    def persistent_storage_service(self) -> PersistentStorageService:
        assert self._persistent_storage_service is not None, "PersistentStorageService is not initialized"
        return self._persistent_storage_service

    @property
    def profile(self) -> Profile:
        assert self._profile is not None, "Profile is not initialized"
        return self._profile

    @property
    def node(self) -> Node:
        assert self._node is not None, "Node is not initialized"
        return self._node

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

    async def setup(self) -> Self:
        self._beekeeper = await self.__setup_beekeeper(remote_endpoint=self._beekeeper_remote_endpoint)
        self._persistent_storage_service = PersistentStorageService(self.beekeeper)
        self._profile = await self._load_profile()
        await self._commands.sync_state_with_beekeeper()
        self._node = Node(self._profile)
        await self._node.setup()
        return self

    async def save_profile_of_world(self) -> None:
        await self.persistent_storage_service.save_profile(self.profile)

    async def close(self) -> None:
        if self._node is not None:
            await self._node.teardown()
        if self._app_state.is_unlocked and self._profile is not None:
            await self.save_profile_of_world()
        if self._beekeeper is not None:
            await self._beekeeper.close()

    def on_going_into_locked_mode(self, source: LockSource) -> None:
        """Triggered when the application is going into the locked mode."""

    def on_going_into_unlocked_mode(self) -> None:
        """Triggered when the application is going into the unlocked mode."""

    async def _load_profile(self) -> Profile:
        profile_name = await self.beekeeper.get_unlocked_profile_name()
        return await self.persistent_storage_service.load_profile(profile_name)

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


class TUIWorld(World, ManualReactive):
    profile: Profile = var(None)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]
    node: Node = var(None)  # type: ignore[assignment]

    async def _load_profile(self) -> Profile:
        try:
            return await super()._load_profile()
        except (BeekeeperNotUnlockedError, ProfileDoesNotExistsError):
            profile = Profile(name=Onboarding.ONBOARDING_PROFILE_NAME)
        return profile

    @property
    def commands(self) -> TUICommands:
        return cast(TUICommands, super().commands)

    @property
    def is_in_onboarding_mode(self) -> bool:
        return self._is_in_onboarding_mode(self.profile)

    def on_going_into_locked_mode(self, source: LockSource) -> None:
        base_message: Final[str] = "Switched to the LOCKED mode"
        if source == "beekeeper_notification_server":
            send_notification = partial(
                self.app.notify,
                f"{base_message} due to inactivity in a temporary unlock mode.",
                timeout=10,
            )
        else:
            send_notification = partial(self.app.notify, f"{base_message}.")

        with contextlib.suppress(ScreenNotFoundError):
            self.app.replace_screen("DashboardUnlocked", "dashboard_locked")
        send_notification()
        self.app.trigger_app_state_watchers()

    def on_going_into_unlocked_mode(self) -> None:
        with contextlib.suppress(ScreenNotFoundError):
            self.app.replace_screen("DashboardLocked", "dashboard_unlocked")
        self.app.notify("Switched to the UNLOCKED mode.")
        self.app.trigger_app_state_watchers()

    async def setup(self) -> Self:
        await super().setup()
        assert self._profile is not None, "Profile is not initialized"
        self.profile = self._profile
        assert self._app_state is not None, "AppState is not initialized"
        self.app_state = self._app_state
        assert self._node is not None, "Node is not initialized"
        self.node = self._node
        return self

    async def save_profile_of_world(self) -> None:
        if not self.is_in_onboarding_mode:
            await super().save_profile_of_world()

    def _is_in_onboarding_mode(self, profile: Profile) -> bool:
        return profile.name == Onboarding.ONBOARDING_PROFILE_NAME

    def _setup_commands(self) -> TUICommands:
        return TUICommands(self)


class CLIWorld(World):
    @property
    def commands(self) -> CLICommands:
        return cast(CLICommands, super().commands)

    def _setup_commands(self) -> CLICommands:
        return CLICommands(self)
