from __future__ import annotations

import asyncio

from clive.__private.si.base import clive_use_unlocked_profile

"""
STEPS BEFORE RUNNING THIS SCRIPT:
1. Run clive beekeeper
2. Export env variables in active console
3. Create profile "alice"
4. Unlock profile "alice"
"""


async def first_script() -> None:
    async with clive_use_unlocked_profile() as clive:
        await clive.show.witnesses("gtg")
        await clive.show.owner_authority("alice")
        await clive.show.active_authority("alice")
        await clive.show.posting_authority("alice")
        balances = await clive.show.balances("alice")
        transfer = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
            broadcast=False,
        )

        profiles = await clive.show.profiles()

    print(f"Balances: {balances}")  # noqa: T201
    print(f"Transfer: {transfer}")  # noqa: T201
    print(f"Profiles: {profiles}")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(first_script())
