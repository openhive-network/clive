from __future__ import annotations

from random import uniform
from typing import TYPE_CHECKING

import test_tools as tt

from clive.__private.core.date_utils import utc_now
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT2_DATA,
    BLOCK_LOG_WITH_CONFIG_DIRECTORY,
    CREATOR_ACCOUNT,
    EMPTY_ACCOUNT,
    KNOWN_EXCHANGES_NAMES,
    PROPOSALS,
    WATCHED_ACCOUNTS_DATA,
    WITNESSES,
    WORKING_ACCOUNT_DATA,
)

if TYPE_CHECKING:
    from pathlib import Path


def prepare_alternate_chain_specs(node: tt.InitNode) -> Path:
    tt.logger.info("Creating alternate chain spec file...")
    current_time = utc_now()
    hardfork_num = int(node.get_version().version.blockchain_version.split(".")[1])
    alternate_chain_specs = tt.AlternateChainSpecs(
        genesis_time=int(current_time.timestamp()),
        hardfork_schedule=[tt.HardforkSchedule(hardfork=hardfork_num, block_num=1)],
        init_supply=20_000_000_000,
        hbd_init_supply=10_000_000_000,
        initial_vesting=tt.InitialVesting(vests_per_hive=1800, hive_amount=10_000_000_000),
    )

    return alternate_chain_specs.export_to_file(BLOCK_LOG_WITH_CONFIG_DIRECTORY)


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
            wallet.api.transfer("initminer", witness.name, tt.Asset.Test(10_000), "memo")
            wallet.api.transfer_to_vesting("initminer", witness.name, tt.Asset.Test(10_000))
            wallet.api.transfer("initminer", witness.name, tt.Asset.Tbd(10_000), memo="memo")

    with wallet.in_single_transaction():
        for witness in WITNESSES:
            wallet.api.update_witness(
                witness.name,
                "https://" + witness.name,
                witness.public_key,
                {
                    "account_creation_fee": tt.Asset.Test(3),
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
            daily_pay = round(uniform(1, 10), 3)  # noqa: S311 # no cryptographic usage
            wallet.api.create_proposal(
                witness.name,
                witness.name,
                tt.Time.from_now(months=start_month, minutes=1),
                tt.Time.from_now(months=end_month, minutes=1),
                tt.Asset.Tbd(daily_pay),
                permlink,
                f"{permlink}",
            )


def create_working_accounts(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating working accounts...")
    wallet.create_account(
        WORKING_ACCOUNT_DATA.account.name,
        hives=WORKING_ACCOUNT_DATA.hives_liquid,
        vests=WORKING_ACCOUNT_DATA.vests,
        hbds=WORKING_ACCOUNT_DATA.hbds_liquid,
    )
    wallet.create_account(
        ALT_WORKING_ACCOUNT1_DATA.account.name,
        hives=ALT_WORKING_ACCOUNT1_DATA.hives_liquid,
        vests=ALT_WORKING_ACCOUNT1_DATA.vests,
        hbds=ALT_WORKING_ACCOUNT1_DATA.hbds_liquid,
    )
    wallet.create_account(
        ALT_WORKING_ACCOUNT2_DATA.account.name,
        hives=ALT_WORKING_ACCOUNT2_DATA.hives_liquid,
        vests=ALT_WORKING_ACCOUNT2_DATA.vests,
        hbds=ALT_WORKING_ACCOUNT2_DATA.hbds_liquid,
    )


def prepare_savings(wallet: tt.Wallet) -> None:
    tt.logger.info("Preparing savings of all accounts...")
    all_accounts = [WORKING_ACCOUNT_DATA, ALT_WORKING_ACCOUNT1_DATA, ALT_WORKING_ACCOUNT2_DATA, *WATCHED_ACCOUNTS_DATA]
    for data in all_accounts:
        if data.hives_savings > 0:
            wallet.api.transfer_to_savings(
                CREATOR_ACCOUNT.name,
                data.account.name,
                data.hives_savings,
                "Supplying HIVE savings",
            )
        if data.hbds_savings > 0:
            wallet.api.transfer_to_savings(
                CREATOR_ACCOUNT.name,
                data.account.name,
                data.hbds_savings,
                "Supplying HBD savings",
            )
        if data.hives_savings_withdrawal > 0:
            wallet.api.transfer_from_savings(
                data.account.name,
                0,
                CREATOR_ACCOUNT.name,
                data.hives_savings_withdrawal,
                "Withdrawing HIVE savings",
            )
        if data.hbds_savings_withdrawal > 0:
            wallet.api.transfer_from_savings(
                data.account.name,
                0,
                CREATOR_ACCOUNT.name,
                data.hbds_savings_withdrawal,
                "Withdrawing HBD savings",
            )


def create_watched_accounts(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating watched accounts...")
    for data in WATCHED_ACCOUNTS_DATA:
        wallet.create_account(
            data.account.name,
            hives=data.hives_liquid,
            vests=data.vests,
            hbds=data.hbds_liquid,
        )


def create_empty_account(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating empty account...")
    wallet.create_account(EMPTY_ACCOUNT.name)


def create_known_exchange_accounts(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating known exchange accounts...")
    for exchange_name in KNOWN_EXCHANGES_NAMES:
        wallet.create_account(
            exchange_name,
        )


def prepare_votes_for_witnesses(wallet: tt.Wallet) -> None:
    tt.logger.info("Prepare votes for witnesses...")
    with wallet.in_single_transaction():
        for i in range(2, 4):
            wallet.api.vote_for_witness(ALT_WORKING_ACCOUNT1_DATA.account.name, WITNESSES[i].name, approve=True)
    with wallet.in_single_transaction():
        for i in range(1, 31):
            wallet.api.vote_for_witness(ALT_WORKING_ACCOUNT2_DATA.account.name, WITNESSES[i].name, approve=True)


def create_example_post_and_vote(wallet: tt.Wallet) -> None:
    tt.logger.info("Creating example post and vote for alice...")
    wallet.api.post_comment(
        WORKING_ACCOUNT_DATA.account.name,
        "example-post",
        "",
        "parent-example-post",
        "Example Post Title",
        "This is an example post body.",
        "{}",
    )
    wallet.api.vote(
        WORKING_ACCOUNT_DATA.account.name,
        WORKING_ACCOUNT_DATA.account.name,
        "example-post",
        100,
    )


def main() -> None:
    node = tt.InitNode()
    configure(node)
    alternate_chain_specs_path = prepare_alternate_chain_specs(node)

    node.run(
        arguments=tt.NodeArguments(alternate_chain_spec=alternate_chain_specs_path),
        time_control=tt.SpeedUpRateTimeControl(5),
    )
    wallet = tt.Wallet(attach_to=node)

    create_witnesses(wallet)
    create_proposals(wallet)
    create_working_accounts(wallet)
    create_watched_accounts(wallet)
    prepare_savings(wallet)
    prepare_votes_for_witnesses(wallet)
    create_example_post_and_vote(wallet)
    create_empty_account(wallet)
    create_known_exchange_accounts(wallet)

    tt.logger.info("Wait 21 blocks to schedule newly created witnesses into future state")
    node.wait_number_of_blocks(21)

    future_witnesses = node.api.database.get_active_witnesses(include_future=True).future_witnesses
    tt.logger.info(f"Future witnesses after voting: {future_witnesses}")

    tt.logger.info("Wait 21 blocks for future state to become active state")
    node.wait_number_of_blocks(21)
    active_witnesses = node.api.database.get_active_witnesses().witnesses
    tt.logger.info(f"Witness state after voting: {active_witnesses}")

    tt.logger.info("Wait to be sure all generated blocks are in block_log.")
    node.wait_for_irreversible_block()

    last_block_number = node.get_last_block_number()
    get_block_response = node.api.block.get_block(block_num=last_block_number).ensure
    timestamp = get_block_response.block.timestamp
    tt.logger.info(f"Final block_log head block number: {last_block_number}")
    tt.logger.info(f"Final block_log head block timestamp: {timestamp}")

    node.close()

    node.block_log.copy_to(BLOCK_LOG_WITH_CONFIG_DIRECTORY)
    node.config.save(BLOCK_LOG_WITH_CONFIG_DIRECTORY)


if __name__ == "__main__":
    main()
