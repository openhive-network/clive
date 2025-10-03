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
        transfer1 = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
            .as_transaction_object()
        )

        # Transfer without signing, just create the transfer
        transfer2 = await clive.process.transfer(
            from_account="alice",
            to_account="gtg",
            amount="1.000 HIVE",
            memo="Test transfer",
        ).as_transaction_object()

        # Transfer with autosign(now normal sign because i have multiple imported keys)
        transfer3 = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with("STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6")
            .as_transaction_object()
        )

        # Transfer with autosign and save to file(now normal sign because i have multiple imported keys)
        transfer4 = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with("STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6")
            .save_file("/workspace/clive_workspace/clive/script_interface_examples/transfer_autosign.json")
        )

        # Transfer with sign and broadcast, should fail due to missing active authority
        try:
            transfer5 = (
                await clive.process.transfer(
                    from_account="alice",
                    to_account="gtg",
                    amount="1.000 HIVE",
                    memo="Test transfer",
                )
                .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
                .broadcast()
            )
        except Exception as e:
            assert (
                "Missing Active Authority aliceTransaction failed to validate using both new (hf26) and legacy serialization'"
                in str(e)
            )

        # Transfer with as_trnsaction_obj, sign and broadcast, should fail due to missing active authority
        transfer10 = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
            .as_transaction_object()
        )

        await transfer10.save_file("/workspace/clive_workspace/clive/script_interface_examples/transfer_autosign2.json")
        try:
            await transfer10.broadcast()
        except Exception as e:
            assert (
                "Missing Active Authority aliceTransaction failed to validate using both new (hf26) and legacy serialization'"
                in str(e)
            )

        # Update active authority
        update_authority = (
            await clive.process.update_active_authority(
                account_name="alice",
                threshold=1,
            )
            .add_account(account_name="gtg", weight=1)
            .as_transaction_object()
        )

        # Transfer with invalid to account, should fail due to validation
        try:
            transfer6 = (
                await clive.process.transfer(
                    from_account="alice",
                    to_account="g",
                    amount="1.000 HIVE",
                    memo="Test transfer",
                )
                .sign_with("STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6")
                .broadcast()
            )
        except Exception as e:
            assert "Expected `str` of length >= 3" in str(e)

        # Transfer with sign with previously saved key, multisign
        transfer7 = (
            await clive.process.transaction(
                from_file="/workspace/clive_workspace/clive/script_interface_examples/transfer_autosign.json",
                already_signed_mode="multisign",
            )
            .sign_with("STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6")
            .as_transaction_object()
        )

        # Transfer with sign with previously saved key, multisign, from object
        transfer_to_load = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
            .as_transaction_object()
        )

        multisigned_transfer = (
            await clive.process.transaction_from_object(
                from_object=transfer_to_load,
                already_signed_mode="multisign",
            )
            .sign_with("STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6")
            .as_transaction_object()
        )

        # Update active authority with add and remove key
        update_authority = (
            await clive.process.update_active_authority(account_name="alice", threshold=11)
            .add_account(account_name="bob", weight=12)
            .add_key(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=13)
            .remove_key(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
            .sign_with("STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6")
            .as_transaction_object()
        )


if __name__ == "__main__":
    asyncio.run(first_script())


# async def first_script() -> None:
#     async with clive_use_unlocked_profile() as clive:

#         add_key_function = partial(add_key, key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr", weight=1)
#         update_function = partial(update_authority, attribute="owner", callback=add_key_function)

#         operation = ProcessAccountUpdate(force=True, account_name="alice", broadcast=True)
#         operation.add_callback(update_function)
#         dupa = await operation._run_in_context_manager()
#         breakpoint()
#         # await operation.run()
#         # await operation.fetch_data()
#         # print(await operation._create_operation())

# if __name__ == "__main__":
#     asyncio.run(first_script())
