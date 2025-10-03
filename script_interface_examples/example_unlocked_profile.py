from __future__ import annotations

import asyncio
from pathlib import Path

from clive.si import clive_use_unlocked_profile

"""
STEPS BEFORE RUNNING THIS SCRIPT:
1. Run clive beekeeper
2. Export env variables in active console
3. Create profile "alice"
4. Unlock profile "alice"
"""


async def example_script() -> None:
    async with clive_use_unlocked_profile() as clive:
        await clive.show.witnesses("bob")
        await clive.show.owner_authority("alice")
        await clive.show.active_authority("alice")
        await clive.show.posting_authority("alice")
        await clive.show.balances("alice")
        await clive.show.profiles()

        transfer = await clive.process.transfer(
            from_account="alice", to_account="bob", amount="1.000 HIVE", memo="Test transfer"
        ).as_transaction_object()

        await (
            clive.process.transaction_from_object(
                from_object=transfer,
                already_signed_mode="override",
            )
            .sign_with("alice_key")
            .save_file(path=Path(__file__).parent / "transfer_tx.json")
        )

        await (
            clive.process.update_active_authority(
                account_name="alice",
                threshold=2,
            )
            .add_key(
                key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr",
                weight=1,
            )
            .as_transaction_object()
        )

        await (
            clive.process.transfer(
                from_account="alice",
                to_account="bob",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .process.transfer(
                from_account="alice",
                to_account="bob",
                amount="2.000 HIVE",
                memo="Test transfer2",
            )
            .sign_with(key="alice_key")
            .as_transaction_object()
        )


if __name__ == "__main__":
    asyncio.run(example_script())
