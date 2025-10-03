from __future__ import annotations

import asyncio
import time

from clive.__private.si.base import clive_use_unlocked_profile


async def first_script() -> None:
    st1 = time.time()
    async with clive_use_unlocked_profile() as clive:
        balances = await clive.show.balances("alice")
        ti = time.time()
        for i in range(1000):
            await clive.process.transfer(
                from_account="alice",
                to_account="mary",
                amount="1.000 HIVE",
                memo=f"Test transfer{i}",
            ).finalize(broadcast=True, sign_with="STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW")
        t2 = time.time()
        after_balances = await clive.show.balances("alice")

    print(f"Hive liquid balance: {balances.hive_liquid.amount}")  # noqa: T201
    print(f"After Hive liquid balance: {after_balances.hive_liquid.amount}")  # noqa: T201
    print(f"Transfer time: {t2 - ti}")  # noqa: T201
    print(f"Total time: {t2 - st1}")  # noqa: T201

    """
    FOR 100 TRANSFERS:
    Hive liquid balance: 99997000
    After Hive liquid balance: 99897000
    Transfer time: 0.9090914726257324 [s]
    Total time: 1.2011473178863525s [s]

    FOR 1000 TRANSFERS:
    Hive liquid balance: 99897000
    After Hive liquid balance: 98897000
    Transfer time: 8.558998346328735 [s]
    Total time: 8.878966569900513 [s]
    """


if __name__ == "__main__":
    asyncio.run(first_script())
