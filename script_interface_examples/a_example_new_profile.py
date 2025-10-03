from __future__ import annotations

import asyncio

from clive.__private.si.base import clive_use_new_profile

"""
STEPS BEFORE RUNNING THIS SCRIPT:
1. Run clive beekeeper
2. Export env variables in active console
"""


async def first_script() -> None:
    async with clive_use_new_profile("radek", "radekradek") as clive:
        balances = await clive.show.balances("radek")
        transfer = await clive.process.transfer(
            from_account="radek",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).as_transaction_object()

        profiles = clive.show.profiles()

    print(f"Balances: {balances}")  # noqa: T201
    print(f"Transfer: {transfer}")  # noqa: T201
    print(f"Profiles: {profiles}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(first_script())
