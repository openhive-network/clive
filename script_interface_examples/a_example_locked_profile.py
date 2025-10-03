from __future__ import annotations

import asyncio

from clive.__private.si.base import clive_unlock_and_use_profile

"""
STEPS BEFORE RUNNING THIS SCRIPT:
1. Run clive beekeeper
2. Export env variables in active console
3. Create profile "alice"
"""


async def first_script() -> None:
    async with clive_unlock_and_use_profile("alice", "alicealice") as clive:
        balances = await clive.show.balances("alice")
        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
            broadcast=False,
        )

        profiles = clive.show.profiles()

    print(f"Balances: {balances}")  # noqa: T201
    print(f"Transfer: {transfer}")  # noqa: T201
    print(f"Profiles: {profiles}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(first_script())
