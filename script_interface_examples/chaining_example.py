from __future__ import annotations

import asyncio

from clive.__private.si.base import clive_use_unlocked_profile


async def first_script() -> None:
    async with clive_use_unlocked_profile() as clive:
        await (
            clive.process.update_owner_authority(
                account_name="alice",
                sign_with="working-key",
                threshold=2,
            )
            .add_account(
                account="other-account",
                weight=1,
            )
            .add_account(
                account="other-account-2",
                weight=1,
            )
            .add_key(
                key="PUBLIC_KEY_STRING",
                weight=1,
            )
            .remove_key(
                key="OLD_PUBLIC_KEY",
            )
            .fire()
        )


if __name__ == "__main__":
    asyncio.run(first_script())
