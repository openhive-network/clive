from __future__ import annotations

import contextlib
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, cast

from textual.reactive import var

from clive.__private.core.app_state import AppState
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.commands import Commands, TextualCommands
from clive.__private.core.communication import Communication
from clive.__private.core.node.node import Node
from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.manual_reactive import ManualReactive
from clive.__private.ui.onboarding.onboarding import Onboarding
from clive.exceptions import ScreenNotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType
    from typing import Literal

    from typing_extensions import Self

    from clive.core.url import Url


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

        self._profile_data = self._load_profile(profile_name)
        self._app_state = AppState(self)
        self._commands = self._setup_commands()

        self._use_beekeeper = use_beekeeper
        self._beekeeper_remote_endpoint = beekeeper_remote_endpoint
        self._beekeeper: Beekeeper | None = None

        self._node = Node(self._profile_data)

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
    def beekeeper(self) -> Beekeeper:
        assert self._beekeeper is not None, "Beekeeper is not initialized"
        return self._beekeeper

    @property
    def node(self) -> Node:
        return self._node

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = Communication.DEFAULT_ATTEMPTS,
        timeout_secs: float = Communication.DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = Communication.DEFAULT_POOL_TIME_SECONDS,
        target: Literal["beekeeper", "node", "all"] = "all",
    ) -> Iterator[None]:
        """Temporarily change connection details."""
        contexts_to_enter = []
        if target in ("beekeeper", "all"):
            contexts_to_enter.append(
                self.beekeeper.modified_connection_details(max_attempts, timeout_secs, pool_time_secs)
            )
        if target in ("node", "all"):
            contexts_to_enter.append(self.node.modified_connection_details(max_attempts, timeout_secs, pool_time_secs))

        with contextlib.ExitStack() as stack:
            for context in contexts_to_enter:
                stack.enter_context(context)
            yield

    async def setup(self) -> Self:
        if self._use_beekeeper:
            self._beekeeper = await self.__setup_beekeeper(remote_endpoint=self._beekeeper_remote_endpoint)
        return self

    async def close(self) -> None:
        self.profile_data.save()
        if self._beekeeper is not None:
            await self._beekeeper.close()

    def _load_profile(self, profile_name: str | None) -> ProfileData:
        return ProfileData.load(profile_name)

    def _setup_commands(self) -> Commands[World]:
        return Commands(self)

    async def __setup_beekeeper(self, *, remote_endpoint: Url | None = None) -> Beekeeper:
        beekeeper = Beekeeper(
            remote_endpoint=remote_endpoint,
            notify_closing_wallet_name_cb=lambda: self.profile_data.name,
        )
        beekeeper.attach_wallet_closing_listener(self)
        await beekeeper.launch()
        return beekeeper

    @property
    def profile_data(self) -> ProfileData:
        return self._profile_data

    @property
    def app_state(self) -> AppState:
        return self._app_state

    def notify_wallet_closing(self) -> None:
        self.app_state.lock()


class TextualWorld(World, ManualReactive):
    profile_data: ProfileData = var(None)  # type: ignore[assignment]
    app_state: AppState = var(None)  # type: ignore[assignment]
    node: Node = var(None)  # type: ignore[assignment]

    def __init__(self) -> None:
        profile_name = (
            ProfileData.get_default_profile_name()
            if ProfileData.is_default_profile_set()
            else Onboarding.ONBOARDING_PROFILE_NAME
        )
        super().__init__(profile_name)
        self.profile_data = self._profile_data
        self.app_state = self._app_state
        self.node = self._node

    def _load_profile(self, profile_name: str | None) -> ProfileData:
        profile = super()._load_profile(profile_name)
        if self._is_in_onboarding_mode(profile):
            profile.skip_saving()
        return profile

    @property
    def commands(self) -> TextualCommands:
        return cast(TextualCommands, super().commands)

    @property
    def is_in_onboarding_mode(self) -> bool:
        return self._is_in_onboarding_mode(self.profile_data)

    def _is_in_onboarding_mode(self, profile_data: ProfileData) -> bool:
        return profile_data.name == Onboarding.ONBOARDING_PROFILE_NAME

    def _setup_commands(self) -> TextualCommands:
        return TextualCommands(self)

    def notify_wallet_closing(self) -> None:
        super().notify_wallet_closing()

        with contextlib.suppress(ScreenNotFoundError):
            self.app.replace_screen("DashboardUnlocked", "dashboard_locked")

        self.app.notify("Switched to the LOCKED mode.", severity="warning", timeout=5)
        self.app.trigger_app_state_watchers()


class TyperWorld(World):
    def _load_profile(self, profile_name: str | None) -> ProfileData:
        return ProfileData.load(profile_name, auto_create=False)
