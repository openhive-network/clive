from __future__ import annotations

import contextlib
from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING, Any, Final, cast

from textual.reactive import var

from clive.__private.cli.exceptions import CLIMultipleWalletsUnlockedError, CLIProfileNotUnlockedError
from clive.__private.core._async import asyncio_run
from clive.__private.core.app_state import AppState, LockSource
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.commands import CLICommands, Commands, TUICommands
from clive.__private.core.commands.exceptions import MultipleWalletsUnlockedError, ProfileNotUnlockedError
from clive.__private.core.communication import Communication
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.known_exchanges import KnownExchanges
from clive.__private.core.node.node import Node
from clive.__private.core.profile import Profile
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_dom_node import CliveDOMNode
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.__private.ui.onboarding.unlock_screen import UnlockScreen
from clive.__private.ui.screens.dashboard import Dashboard

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
        self._commands = self._setup_commands()

        self._beekeeper: Beekeeper | None = None
        self._profile: Profile | None = None
        self._node: Node | None = None

        self._app_state: AppState
        app_state = AppState(self)
        self.set_app_state(app_state)

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
        profile = await self._load_profile()
        self.set_profile(profile)
        if safe_settings.beekeeper.is_session_token_set:
            await self._commands.sync_state_with_beekeeper()
        node = Node(self.profile)
        self.set_node(node)
        await self.node.setup()
        return self

    def set_app_state(self, app_state: AppState) -> None:
        self._app_state = app_state

    def set_node(self, node: Node) -> None:
        self._node = node

    def set_profile(self, profile: Profile) -> None:
        self._profile = profile

    async def close(self) -> None:
        await self.node.teardown()
        await self._save_profile(self.profile)
        await self.beekeeper.close()

    def on_going_into_locked_mode(self, source: LockSource) -> None:
        """Triggered when the application is going into the locked mode."""

    def on_going_into_unlocked_mode(self) -> None:
        """Triggered when the application is going into the unlocked mode."""

    async def _load_profile(self) -> Profile:
        encryption_service = await EncryptionService.from_beekeeper(self.beekeeper)
        return await Profile.load(encryption_service)

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

    async def _save_profile(self, profile: Profile) -> None:
        try:
            encryption_service = await EncryptionService.from_beekeeper(self.beekeeper)
            await profile.save(encryption_service)
        except ProfileNotUnlockedError:
            logger.warning(
                "Profile is not saved because beekeeper session is not unlocked, maybe beekeeper session expired."
            )


class TUIWorld(World, CliveDOMNode):
    profile: Profile = var(None)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]
    node: Node = var(None)  # type: ignore[assignment]

    def set_app_state(self, app_state: AppState) -> None:
        super().set_app_state(app_state)
        self.app_state = app_state

    def set_node(self, node: Node) -> None:
        super().set_node(node)
        self.node = node

    def set_profile(self, profile: Profile) -> None:
        super().set_profile(profile)
        self.profile = profile

    async def _load_profile(self) -> Profile:
        try:
            return await super()._load_profile()
        except ProfileNotUnlockedError:
            profile = Profile(name=Onboarding.ONBOARDING_PROFILE_NAME)
        return profile

    @property
    def commands(self) -> TUICommands:
        return cast(TUICommands, super().commands)

    @property
    def is_in_onboarding_mode(self) -> bool:
        return self._is_in_onboarding_mode(self.profile)

    def clear_profile(self, *, trigger_profile_watchers: bool = False) -> None:
        """Set the profile to default (Onboarding) with optional triggering of profile watchers."""
        profile = Profile(name=Onboarding.ONBOARDING_PROFILE_NAME)
        if trigger_profile_watchers:
            self.profile = profile
            return

        self.set_reactive(self.__class__.profile, profile)  # type: ignore[arg-type]

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

        send_notification()
        if self.app.is_world_set:
            self.app.trigger_app_state_watchers()

        asyncio_run(self._save_profile(self.profile))
        self.clear_profile()

        self._add_welcome_modes()
        self.app.switch_mode("unlock")
        self._restart_dashboard_mode()

    def on_going_into_unlocked_mode(self) -> None:
        if self.app.is_world_set:
            self.app.notify("Switched to the UNLOCKED mode.")
            self.app.trigger_app_state_watchers()

    def _is_in_onboarding_mode(self, profile: Profile) -> bool:
        return profile.name == Onboarding.ONBOARDING_PROFILE_NAME

    def _setup_commands(self) -> TUICommands:
        return TUICommands(self)

    def _add_welcome_modes(self) -> None:
        self.app.add_mode("onboarding", Onboarding)
        self.app.add_mode("unlock", UnlockScreen)

    def _restart_dashboard_mode(self) -> None:
        self.app.remove_mode("dashboard")
        self.app.add_mode("dashboard", Dashboard)

    async def _save_profile(self, profile: Profile) -> None:
        if not self.is_in_onboarding_mode:
            await super()._save_profile(profile)


class CLIWorld(World):
    @property
    def commands(self) -> CLICommands:
        return cast(CLICommands, super().commands)

    def _setup_commands(self) -> CLICommands:
        return CLICommands(self)

    async def _load_profile(self) -> Profile:
        try:
            return await super()._load_profile()
        except ProfileNotUnlockedError as error:
            raise CLIProfileNotUnlockedError from error
        except MultipleWalletsUnlockedError as error:
            raise CLIMultipleWalletsUnlockedError from error
