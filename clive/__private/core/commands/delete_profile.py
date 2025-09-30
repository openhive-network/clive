from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.lock import Lock
from clive.__private.core.profile import Profile

if TYPE_CHECKING:
    from beekeepy.asynchronous import AsyncSession


@dataclass(kw_only=True)
class DeleteProfile(Command):
    """
    Delete profile and lock if it was unlocked.

    Attributes:
        profile_name_to_delete: The name of the profile to delete.
        profile_name_currently_unlocked: The name of the currently unlocked profile, if any.
        session: The session to use for locking, if needed.
        force: If True, remove all profile versions, also not migrated/backed-up.
            If False and multiple versions or back-ups exist, raise error.

    """

    profile_name_to_delete: str
    profile_name_currently_unlocked: str | None
    session: AsyncSession | None
    force: bool = False

    async def _execute(self) -> None:
        Profile.delete_by_name(self.profile_name_to_delete, force=self.force)
        if self.profile_name_to_delete == self.profile_name_currently_unlocked:
            assert self.session is not None, "Session must be provided to delete currently unlocked profile"
            await Lock(session=self.session).execute()
