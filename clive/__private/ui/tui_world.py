from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from textual.reactive import var

from clive.__private.core.commands.commands import TUICommands
from clive.__private.core.commands.get_unlocked_user_wallet import NoProfileUnlockedError
from clive.__private.core.world import World
from clive.__private.ui.clive_dom_node import CliveDOMNode

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState, LockSource
    from clive.__private.core.node import Node
    from clive.__private.core.profile import Profile


class TUIWorld(World, CliveDOMNode):
    profile_reactive: Profile = var(None, init=False)  # type: ignore[assignment]
    """Should be used only after unlocking the profile so it will be available then."""

    node_reactive: Node = var(None, init=False)  # type: ignore[assignment]
    """Should be used only after unlocking the profile so it will be available then."""

    app_state: AppState = var(None, init=False)  # type: ignore[assignment]

    @override
    def __init__(self) -> None:
        super().__init__()
        self.app_state = self._app_state

    @property
    def commands(self) -> TUICommands:
        return cast("TUICommands", super().commands)

    @property
    def _should_save_profile_on_close(self) -> bool:
        """In TUI, it's not possible to save profile on some screens like Unlock/CreateProfile."""
        return super()._should_save_profile_on_close and self.app_state.is_unlocked

    @override
    async def _setup(self) -> None:
        """
        In TUIWorld we assume that profile (and node) is always loaded when entering context manager.

        It's initialized with None because reactive attribute initialization can't be delayed otherwise.
        """
        await super()._setup()
        try:
            await self.load_profile_based_on_beekepeer()
        except NoProfileUnlockedError:
            await self.switch_profile(None)

    async def switch_profile(self, new_profile: Profile | None) -> None:
        await super().switch_profile(new_profile)
        self._update_profile_related_reactive_attributes()

    def _watch_profile(self, profile: Profile) -> None:
        self.node.change_related_profile(profile)

    async def _on_going_into_locked_mode(self, source: LockSource) -> None:
        await self.app._switch_mode_into_locked(source)

    def _setup_commands(self) -> TUICommands:
        return TUICommands(self)

    def _update_profile_related_reactive_attributes(self) -> None:
        # There's no proper way to add some proxy reactive property on textual reactives that could raise error if
        # not set yet, and still can be watched. See: https://github.com/Textualize/textual/discussions/4007

        if not self.is_node_available or not self.is_profile_available:
            assert not self.app_state.is_unlocked, "Profile and node should never be None when unlocked"

        self.node_reactive = self._node  # type: ignore[assignment] # ignore that,  node_reactive shouldn't be accessed before unlocking
        self.profile_reactive = self._profile  # type: ignore[assignment] # ignore that, profile_reactive shouldn't be accessed before unlocking
