from __future__ import annotations

import asyncio

from clive.__private.si.base import clive_use_unlocked_profile


async def first_script() -> None:
    async with clive_use_unlocked_profile() as clive:
        double_transfer = (
            await clive.process.transfer(
                from_account="alice",
                to_account="gtg",
                amount="1.000 HIVE",
                memo="Test transfer",
            )
            .sign_with(key="alice")
            .as_transaction_object()
        )
        # combined = (
        #     await clive.process.update_active_authority(
        #         account_name="alice",
        #         threshold=2,
        #     )
        #     .add_key(
        #         key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr",
        #         weight=1,
        #     )
        #     .process.transfer(
        #         from_account="alice",
        #         to_account="bob",
        #         amount="5.000 HIVE",
        #         memo="Transfer after authority update",
        #     )
        #     .save_file(path="/workspace/clive_workspace/clive/script_interface_examples/combined_transaction.bin", format="bin", serialization_mode="hf26")
        # )

    #     read_from_file = (
    #         await clive.process.transaction(
    #             from_file="/workspace/clive_workspace/clive/script_interface_examples/test_alice.json",
    #             already_signed_mode="multisign",
    #             # ).process.transfer(
    #             #         from_account="alice",
    #             #         to_account="bob",
    #             #         amount="5.000 HIVE",
    #             #         memo="Transfer after authority update",
    #         )
    #         .sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr")
    #         .sign_with(key="STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6")
    #         .as_transaction_object()
    #     )
    # print(read_from_file)

    #     transfer1 = await clive.process.transfer(
    #         from_account="alice",
    #         to_account="gtg",
    #         amount="1.000 HIVE",
    #         memo="Test transfer",
    #     ).sign_with(key="STM5iuVuYcsZmCzXHJT9VbVvHATPa28cLMrf5zKEkzqKc73e22Jtr").as_transaction_object()

    #     transfer7 = await clive.process.transaction_from_object(
    #         from_object=transfer1,
    #         already_signed_mode="multisign",
    #     ).sign_with("STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6").as_transaction_object()
    # print(transfer7)


if __name__ == "__main__":
    asyncio.run(first_script())

# 5JRYrSChVpb1941WF7zR1a1x4Lema1N64DG4BaHvDZFU2fHASSh
# STM7VP64ZMwv3r322WU6YsZLBgp2dFCR9oorNkPp872rhPRgCHHU6
