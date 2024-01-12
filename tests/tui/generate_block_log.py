from __future__ import annotations

import os
import sys
from pathlib import Path
from random import randint

import test_tools as tt

from clive_local_tools.tui.constants import WATCHED_ACCOUNTS, WITNESSES_40, WORKING_ACCOUNT


def create_working_account(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating working account...")
    wallet.create_account(
        WORKING_ACCOUNT.name,
        hives=tt.Asset.Test(1000).as_nai(),
        vests=tt.Asset.Test(1000).as_nai(),
        hbds=tt.Asset.Tbd(1000).as_nai(),
    )
    # Supplying savings:
    wallet.api.transfer_to_savings(
        WORKING_ACCOUNT.name,
        WORKING_ACCOUNT.name,
        tt.Asset.Test(100).as_nai(),
        "Supplying HIVE savings",
    )
    wallet.api.transfer_to_savings(
        WORKING_ACCOUNT.name,
        WORKING_ACCOUNT.name,
        tt.Asset.Tbd(100).as_nai(),
        "Supplying HBD savings",
    )
    account = wallet.api.get_account(WORKING_ACCOUNT.name)
    tt.logger.debug(f"account: {account}")


def create_watched_accounts(wallet: tt.Wallet) -> None:
    def random_amount() -> int:
        return randint(1_000, 5_000)

    tt.logger.info("Creating watched accounts...")
    for account in WATCHED_ACCOUNTS:
        wallet.create_account(
            account.name,
            hives=tt.Asset.Test(random_amount()).as_nai(),
            vests=tt.Asset.Test(random_amount()).as_nai(),
            hbds=tt.Asset.Tbd(random_amount()).as_nai(),
        )


def create_witness_accounts(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating witness accounts...")
    amount = 10_000
    for witness in WITNESSES_40:
        wallet.create_account(
            witness.name,
            hives=tt.Asset.Test(amount).as_nai(),
            vests=tt.Asset.Test(amount).as_nai(),
            hbds=tt.Asset.Tbd(amount).as_nai(),
        )
        wallet.api.update_witness(
            witness.name,
            "http://url.html",
            witness.public_key,
            {
                "account_creation_fee": tt.Asset.Test(10).as_nai(),
                "maximum_block_size": 131072,
                "hbd_interest_rate": 1000,
            },
        )
        amount -= 10


def create_witnesses_list(number: int) -> list[str]:
    assert number > 0, f"create_witnesses_list number should be greater than 0 (current is: {number})."
    assert number < 10_000, f"create_witnesses_list number should be less than 10_000 (current is: {number})."
    suffix_width = 1
    suffix_width += number > 9
    suffix_width += number > 99
    suffix_width += number > 999

    result = []
    for i in range(number):
        result.append(f"witness-{i+1:0{suffix_width}d}")
    return result


def generate_blocks(node: tt.Node, count: int = 1) -> None:
    node.api.debug_node.debug_generate_blocks(debug_key=tt.Account("initminer").private_key, count=count)


def vote_for_witnesses(wallet: tt.Wallet, account_to_vote_with: str, witnesses_to_vote_for: list[str]) -> None:
    tt.logger.info(f"{account_to_vote_with} votes for {witnesses_to_vote_for}...")
    for witness_to_vote_for in witnesses_to_vote_for:
        wallet.api.vote_for_witness(account_to_vote_with, witness_to_vote_for, True)


def main() -> None:
    """
    Required blockchain state:
    1. There is at least 40 witnesses (witness_01, wintess_02...). The first one should have more voted HP than the second, etc.
    2. 4 regular users:
        - User 1 hasn't voted for any witnesses.
        - User 2 has voted for two witnesses (witness_02 and witness_03).
        - User 3 has voted for 30 witnesses.
        - User 4 has voted for 30 witnesses.
    """
    block_log_dir = Path(__file__).resolve().parent / "generated"  # default path required by test-tools
    if not block_log_dir.exists():
        os.mkdir(block_log_dir)

    node = tt.InitNode()
    node.config.enable_stale_production = True
    node.config.required_participation = 0
    node.run()

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    for key in node.config.private_key:
        wallet.api.import_key(key)

    create_working_account(wallet)  # 1. user
    create_watched_accounts(wallet)  # 2..4 users
    #create_witness_accounts(wallet)  # 40 witness accounts

    witnesses = ["initminer"]
    #witnesses.extend([acc.name for acc in WITNESSES_40])

    #vote_for_witnesses(wallet, WATCHED_ACCOUNTS[0].name, witnesses[2:4])
    #vote_for_witnesses(wallet, WATCHED_ACCOUNTS[1].name, witnesses[1:31])
    #vote_for_witnesses(wallet, WATCHED_ACCOUNTS[2].name, witnesses[11:41])

    result = wallet.list_accounts()
    tt.logger.info(f"accounts: {result}")
    last_block = node.get_last_block_number()
    generate_blocks(node, 30)
    node.wait_for_irreversible_block(last_block)
    tt.logger.info(f"last block number: {node.get_last_block_number()}")
    result = node.api.database.list_witnesses(start="", limit=100, order="by_name")["witnesses"]
    tt.logger.info(f"witnesses: {result}")

    wallet.close()
    node.close()

    sys.exit(0)


if __name__ == "__main__":
    main()
