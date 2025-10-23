from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.si.validators import ProfileNameValidator, SetPasswordValidator
from clive.__private.si.core.base import CommandBase

if TYPE_CHECKING:
    from clive.__private.core.world import World

class ProfileCreate(CommandBase[None]):
    def __init__(self, world: World, profile_name: str, password: str) -> None:
        self.world = world
        self.profile_name = profile_name
        self.password = password

    def validate(self):
        ProfileNameValidator().validate(self.profile_name)
        SetPasswordValidator().validate(self.password)

    async def _run(self) -> None:
        await self.world.create_new_profile_with_wallets(self.profile_name, self.password)


class ProfileLoad(CommandBase[None]):
    def __init__(self, world: World) -> None:
        self.world = world

    async def _run(self) -> None:
        await self.world.load_profile_based_on_beekepeer()


class ProfileUnlockAndLoad(CommandBase[None]):
    def __init__(self, world: World, profile_name: str, password: str) -> None:
        self.world = world
        self.profile_name = profile_name
        self.password = password

    def validate(self):
        ProfileNameValidator().validate(self.profile_name)
        SetPasswordValidator().validate(self.password)

    async def _run(self) -> None:
        await self.world.load_profile(profile_name=self.profile_name, password=self.password)
