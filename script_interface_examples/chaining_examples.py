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
        # Transfer with sign with previous imported key, strict
        transfer1 = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).finalize(sign_with="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", broadcast=False)

        # Transfer without signing, just create the transfer
        transfer2 = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).finalize(broadcast=False)

        # Transfer with autosign
        transfer3 = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).finalize(autosign=True, broadcast=False)

        # Transfer with autosign and save to file
        transfer4 = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).finalize(
            autosign=True,
            save_file="/workspace/clive_workspace/clive/script_interface_examples/transfer.json",
            broadcast=False,
        )

        # Transfer with sign and broadcast, should fail due to missing active authority
        try:
            transfer5 = await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            ).finalize(sign_with="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", broadcast=True)
        except Exception as e:
            assert (
                "Missing Active Authority aliceTransaction failed to validate using both new (hf26) and legacy serialization'"
                in str(e)
            )

        # # Update active authority, should fail due to not implemented method
        # try:
        #     update_authority = await clive.process.update_active_authority(
        #         account_name="alice",
        #         threshold=1,
        #     ).add_account(account_name="gtg", weight=1).finalize(broadcast=False)
        # except Exception as e:
        #     assert "Not implemented yet gtg, 1" in str(e)

        # Transfer with invalid to account, should fail due to validation
        try:
            transfer6 = await clive.process.transfer(
                from_account="alice",
                to_account="g",
                amount="1.000 HIVE",
                memo="Test transfer",
            ).finalize(broadcast=False)
        except Exception as e:
            assert "Expected `str` of length >= 3" in str(e)

        transfer7 = await clive.process.transaction(
            from_file="/workspace/clive_workspace/clive/script_interface_examples/transfer.json",
            force_unsign=False,
        ).finalize(autosign=True, broadcast=False)

        update_authority = (
            await clive.process.update_active_authority(account_name="alice", threshold=11)
            .add_account(account_name="bob", weight=12)
            .add_key(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=13)
            .finalize(broadcast=False)
        )
        print("duda", update_authority)


if __name__ == "__main__":
    asyncio.run(first_script())
