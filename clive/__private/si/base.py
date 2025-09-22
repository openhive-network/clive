from clive.__private.core.world import World


class CliveSi:
    def __init__(self) -> None:
        from clive.__private.si.show import ShowInterface
        self.world =  World()
        self.show = ShowInterface(self)

    async def setup(self) -> None:
        await self.world.setup()

    async def create_new_profile(self, profile_name: str) -> None:
        await self.world.create_new_profile(profile_name)


