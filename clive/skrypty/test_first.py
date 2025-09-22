from __future__ import annotations

import loguru

from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.world import World


async def test_first() -> None:
    world = World()
    await world.setup()
    await world.create_new_profile("alice")

    # pokazywanie profili
    show_profile = world.profile

    # pokazywanie balansów
    account = TrackedAccount(name="alice")

    await world.commands.update_node_data(accounts=[account])
    balances = account.data
    loguru.logger.info(balances)
    loguru.logger.info(show_profile)
