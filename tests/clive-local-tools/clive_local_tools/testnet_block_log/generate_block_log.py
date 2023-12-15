from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from random import uniform

import test_tools as tt

from clive_local_tools.testnet_block_log.constants import (
    CREATOR_ACCOUNT,
    PROPOSALS,
    WATCHED_ACCOUNTS,
    WITNESSES,
    WORKING_ACCOUNT,
)


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
    for name in WITNESSES:
        node.config.witness.append(name)
        node.config.private_key.append(tt.Account(name).private_key)
    node.config.plugin.append("account_history_rocksdb")
    node.config.plugin.append("account_history_api")
    node.config.plugin.append("reputation_api")
    node.config.plugin.append("rc_api")
    node.config.plugin.append("transaction_status_api")


def create_witnesses(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating witnesses...")
    for name in WITNESSES:
        wallet.api.import_key(tt.PrivateKey(name))

    with wallet.in_single_transaction():
        for name in WITNESSES:
            key = tt.PublicKey(name)
            wallet.api.create_account_with_keys("initminer", name, "{}", key, key, key, key)

    with wallet.in_single_transaction():
        for name in WITNESSES:
            wallet.api.transfer("initminer", name, tt.Asset.Test(10_000).as_nai(), "memo")
            wallet.api.transfer_to_vesting("initminer", name, tt.Asset.Test(10_000).as_nai())
            wallet.api.transfer("initminer", name, tt.Asset.Tbd(10_000).as_nai(), memo="memo")

    with wallet.in_single_transaction():
        for name in WITNESSES:
            wallet.api.update_witness(
                name,
                "https://" + name,
                tt.Account(name).public_key,
                {
                    "account_creation_fee": tt.Asset.Test(3).as_nai(),
                    "maximum_block_size": 65536,
                    "hbd_interest_rate": 0,
                },
            )


def create_proposals(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating proposals...")
    with wallet.in_single_transaction():
        for account_name, proposal in zip(WITNESSES, PROPOSALS, strict=False):
            permlink = proposal
            wallet.api.post_comment(
                account_name, f"{permlink}", "", f"parent-{permlink}", f"{permlink}-title", f"{permlink}-body", "{}"
            )
    with wallet.in_single_transaction():
        for i, (account_name, proposal) in enumerate(zip(WITNESSES, PROPOSALS, strict=False)):
            # create proposal with permlink pointing to comment
            permlink = proposal
            start_month = i - 1
            end_month = i
            daily_pay = round(uniform(1, 10), 3)
            wallet.api.create_proposal(
                account_name,
                account_name,
                tt.Time.from_now(months=start_month, minutes=1),
                tt.Time.from_now(months=end_month, minutes=1),
                tt.Asset.Tbd(daily_pay).as_nai(),
                permlink,
                f"{permlink}",
            )


def create_working_account(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating working account...")
    wallet.create_account(
        WORKING_ACCOUNT.name,
        hives=tt.Asset.Test(100_000).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
        vests=tt.Asset.Test(100_000).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
        hbds=tt.Asset.Tbd(100_000).as_nai(),  # type: ignore[arg-type]  # test-tools dooesn't convert to hf26
    )


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
    )
    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])

    create_witnesses(wallet)
    create_proposals(wallet)
    create_working_account(wallet)
    prepare_savings(wallet)
    create_watched_accounts(wallet)
    send_test_transfer_from_working_account(wallet)

    tt.logger.info("Wait 21 blocks to schedule newly created witnesses into future state")
    node.wait_number_of_blocks(21)

    future_witnesses = node.api.database.get_active_witnesses(include_future=True)["future_witnesses"]  # type: ignore[call-arg]
    tt.logger.info(f"Future witnesses after voting: {future_witnesses}")

    tt.logger.info("Wait 21 blocks for future state to become active state")
    node.wait_number_of_blocks(21)

    active_witnesses = node.api.database.get_active_witnesses()["witnesses"]
    tt.logger.info(f"Witness state after voting: {active_witnesses}")

    # Reason of this wait is to enable moving forward of irreversible block
    tt.logger.info("Wait 21 blocks (when every witness sign at least one block)")
    node.wait_number_of_blocks(21)

    timestamp = node.api.block.get_block(block_num=node.get_last_block_number())["block"]["timestamp"]
    tt.logger.info(f"Final block_log head block number: {node.get_last_block_number()}")
    tt.logger.info(f"Final block_log head block timestamp: {timestamp}")

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
