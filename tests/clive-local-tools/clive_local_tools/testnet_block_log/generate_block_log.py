from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from random import uniform
from typing import Final

import test_tools as tt

from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1,
    ALT_WORKING_ACCOUNT1_WITNESS_VOTES_COUNT,
    ALT_WORKING_ACCOUNT1_WITNESS_VOTES_START,
    ALT_WORKING_ACCOUNT2,
    ALT_WORKING_ACCOUNT2_WITNESS_VOTES_COUNT,
    ALT_WORKING_ACCOUNT2_WITNESS_VOTES_START,
    CREATOR_ACCOUNT,
    PROPOSALS,
    WATCHED_ACCOUNTS,
    WITNESSES,
    WORKING_ACCOUNT,
)

WORKING_ACCOUNT_INITIAL_BALANCE: Final[int] = 100_000
WORKING_ACCOUNT_INITIAL_BALANCE_INCREMENT: Final[int] = 10_000
EXTRA_TIME_SHIFT_FOR_GOVERNANCE: Final[timedelta] = timedelta(days=1)


def set_vest_price_by_alternate_chain_spec(node: tt.InitNode, file_path: Path) -> None:
    tt.logger.info("Creating alternate chain spec file...")
    current_time = datetime.now()
    hardfork_num = int(node.get_version()["version"]["blockchain_version"].split(".")[1])
    alternate_chain_spec_content = {
        "genesis_time": int(current_time.timestamp()),
        "hardfork_schedule": [{"hardfork": hardfork_num, "block_num": 1}],
        "init_supply": 20_000_000_000,
        "hbd_init_supply": 10_000_000_000,
        "initial_vesting": {"vests_per_hive": 1800, "hive_amount": 10_000_000_000},
    }

    with file_path.open("w") as json_file:
        json.dump(alternate_chain_spec_content, json_file, indent=2)


def configure(node: tt.InitNode) -> None:
    tt.logger.info("Creating node config...")
    for witness in WITNESSES:
        node.config.witness.append(witness.name)
        node.config.private_key.append(witness.private_key)
    node.config.plugin.append("account_history_rocksdb")
    node.config.plugin.append("account_history_api")
    node.config.plugin.append("reputation_api")
    node.config.plugin.append("rc_api")
    node.config.plugin.append("transaction_status_api")


def create_witnesses(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating witnesses...")
    for witness in WITNESSES:
        wallet.api.import_key(witness.private_key)

    with wallet.in_single_transaction():
        for witness in WITNESSES:
            key = witness.public_key
            wallet.api.create_account_with_keys("initminer", witness.name, "{}", key, key, key, key)

    with wallet.in_single_transaction():
        for witness in WITNESSES:
            wallet.api.transfer("initminer", witness.name, tt.Asset.Test(10_000).as_nai(), "memo")
            wallet.api.transfer_to_vesting("initminer", witness.name, tt.Asset.Test(10_000).as_nai())
            wallet.api.transfer("initminer", witness.name, tt.Asset.Tbd(10_000).as_nai(), memo="memo")

    with wallet.in_single_transaction():
        for witness in WITNESSES:
            wallet.api.update_witness(
                witness.name,
                "https://" + witness.name,
                witness.public_key,
                {
                    "account_creation_fee": tt.Asset.Test(3).as_nai(),
                    "maximum_block_size": 65536,
                    "hbd_interest_rate": 0,
                },
            )


def create_proposals(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating proposals...")
    with wallet.in_single_transaction():
        for witness, proposal in zip(WITNESSES, PROPOSALS, strict=False):
            permlink = proposal
            wallet.api.post_comment(
                witness.name, f"{permlink}", "", f"parent-{permlink}", f"{permlink}-title", f"{permlink}-body", "{}"
            )
    with wallet.in_single_transaction():
        for i, (witness, proposal) in enumerate(zip(WITNESSES, PROPOSALS, strict=False)):
            # create proposal with permlink pointing to comment
            permlink = proposal
            start_month = i - 1
            end_month = i
            daily_pay = round(uniform(1, 10), 3)
            wallet.api.create_proposal(
                witness.name,
                witness.name,
                tt.Time.from_now(months=start_month, minutes=1),
                tt.Time.from_now(months=end_month, minutes=1),
                tt.Asset.Tbd(daily_pay).as_nai(),
                permlink,
                f"{permlink}",
            )


def create_working_accounts(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating working accounts...")
    account_balance = WORKING_ACCOUNT_INITIAL_BALANCE
    for account_name in (WORKING_ACCOUNT.name, ALT_WORKING_ACCOUNT1.name, ALT_WORKING_ACCOUNT2.name):
        wallet.create_account(
            account_name,
            hives=tt.Asset.Test(account_balance).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
            vests=tt.Asset.Test(account_balance).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
            hbds=tt.Asset.Tbd(account_balance).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
        )
        account_balance += WORKING_ACCOUNT_INITIAL_BALANCE_INCREMENT


def prepare_savings(wallet: tt.Wallet) -> None:
    tt.logger.info("Preparing savings of working account...")
    wallet.api.transfer_to_savings(
        WORKING_ACCOUNT.name,
        WORKING_ACCOUNT.name,
        tt.Asset.Test(100).as_nai(),
        "Supplying HIVE savings",
    )
    wallet.api.transfer_to_savings(
        WORKING_ACCOUNT.name,
        WORKING_ACCOUNT.name,
        tt.Asset.Tbd(123).as_nai(),
        "Supplying HBD savings",
    )
    # Number of transfer_from_savings for WORKING_ACCOUNT should be equal to clive_local_tools.testnet_block_log.constants.WORKING_ACCOUNT_FROM_SAVINGS_TRANSFERS_COUNT
    wallet.api.transfer_from_savings(
        WORKING_ACCOUNT.name,
        0,
        WORKING_ACCOUNT.name,
        tt.Asset.Tbd(23).as_nai(),
        "Withdrawing HBD savings",
    )


def create_watched_accounts(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating watched accounts...")
    for account in WATCHED_ACCOUNTS:
        wallet.create_account(
            account.name,
            hives=tt.Asset.Test(1_000).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
            vests=tt.Asset.Test(1_000).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
            hbds=tt.Asset.Tbd(1_000).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
        )


def send_test_transfer_from_working_account(wallet: tt.Wallet) -> None:
    tt.logger.info("Sending test transfer...")
    wallet.api.transfer(WORKING_ACCOUNT.name, CREATOR_ACCOUNT.name, tt.Asset.Test(1).as_nai(), memo="memo")


def prepare_votes_for_witnesses(wallet: tt.Wallet) -> None:
    tt.logger.info("Prepare votes for witnesses...")
    with wallet.in_single_transaction():
        for i in range(
            ALT_WORKING_ACCOUNT1_WITNESS_VOTES_START,
            ALT_WORKING_ACCOUNT1_WITNESS_VOTES_COUNT + ALT_WORKING_ACCOUNT1_WITNESS_VOTES_START,
        ):
            wallet.api.vote_for_witness(ALT_WORKING_ACCOUNT1.name, WITNESSES[i].name, True)
    with wallet.in_single_transaction():
        for i in range(
            ALT_WORKING_ACCOUNT2_WITNESS_VOTES_START,
            ALT_WORKING_ACCOUNT2_WITNESS_VOTES_COUNT + ALT_WORKING_ACCOUNT2_WITNESS_VOTES_START,
        ):
            wallet.api.vote_for_witness(ALT_WORKING_ACCOUNT2.name, WITNESSES[i].name, True)


def main() -> None:
    directory = Path(__file__).parent.absolute()
    node = tt.InitNode()
    configure(node)
    set_vest_price_by_alternate_chain_spec(node, directory / "alternate-chain-spec.json")

    node.run(
        arguments=[
            "--alternate-chain-spec",
            str(directory / "alternate-chain-spec.json"),
        ],
        time_control="+0h x5",
    )
    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])

    create_witnesses(wallet)
    create_proposals(wallet)
    create_working_accounts(wallet)
    create_watched_accounts(wallet)
    prepare_savings(wallet)
    prepare_votes_for_witnesses(wallet)
    send_test_transfer_from_working_account(wallet)

    tt.logger.info("Wait 21 blocks to schedule newly created witnesses into future state")
    node.wait_number_of_blocks(21)

    future_witnesses = node.api.database.get_active_witnesses(include_future=True)["future_witnesses"]  # type: ignore[call-arg]
    tt.logger.info(f"Future witnesses after voting: {future_witnesses}")

    tt.logger.info("Wait 21 blocks for future state to become active state")
    node.wait_number_of_blocks(21)
    active_witnesses = node.api.database.get_active_witnesses()["witnesses"]
    tt.logger.info(f"Witness state after voting: {active_witnesses}")

    tt.logger.info("Wait to be sure all generated blocks are in block_log.")
    node.wait_for_irreversible_block()

    last_block_number = node.get_last_block_number()
    timestamp = node.api.block.get_block(block_num=last_block_number)["block"]["timestamp"]
    tt.logger.info(f"Final block_log head block number: {last_block_number}")
    tt.logger.info(f"Final block_log head block timestamp: {timestamp}")

    timestamp += EXTRA_TIME_SHIFT_FOR_GOVERNANCE

    tt.logger.info(f"Final block_log shifted timestamp: {timestamp}")

    with (directory / "timestamp").open("w", encoding="utf-8") as file:
        file.write(f"@{timestamp}")

    node.close()

    blockchain_directory = directory / "blockchain"
    blockchain_directory.mkdir(parents=True, exist_ok=True)
    node.block_log.copy_to(blockchain_directory)

    # notifications port should be picked randomly when starting node to avoid port collision
    node.config.notifications_endpoint = None
    config_file = directory / "config.ini"
    node.config.write_to_file(config_file)


if __name__ == "__main__":
    main()
