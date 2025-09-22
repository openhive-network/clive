from __future__ import annotations
import asyncio
from py_compile import main

import loguru

from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.core.world import World
from clive.__private.cli.commands.process.transfer import Transfer
from schemas.operations.transfer_operation import TransferOperation
from schemas.fields.assets import AssetHbd

async def first_function() -> None:
    world = World()
    # await world.setup()
    await world.create_new_profile("alice")

    # pokazywanie profili
    show_profile = world.profile

    # pokazywanie balansów
    account = TrackedAccount(name="alice")

    await world.commands.update_node_data(accounts=[account])
    balances = account.data
    loguru.logger.info(balances)
    loguru.logger.info(show_profile)

    #transferowanie
    transfer_operation = TransferOperation(
            from_="alice",
            to="gtg",
            amount=AssetHbd(amount=10000),
            memo="memo",
        )
    
    trx = (await world.commands.perform_actions_on_transaction(
                content=transfer_operation,
                broadcast=False,
            )).result_or_raise
    pass
    # await Transfer(from_account="alice", to="gtg", amount="1.000 HIVE", memo="Test transfer", broadcast=False).run()()

if __name__ == "__main__":
    asyncio.run(first_function())