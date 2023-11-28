from __future__ import annotations

import argparse
import asyncio
import shutil
import sys
import time
from typing import TYPE_CHECKING

import test_tools as tt

from clive.__private.config import settings
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.storage.accounts import Account as WatchedAccount
from clive.__private.storage.accounts import WorkingAccount
from clive.main import _main as clive_main
from clive_local_tools.constants import TESTNET_CHAIN_ID
from clive_local_tools.testnet_block_log import (
    get_alternate_chain_spec_path,
    get_block_log,
    get_config,
)
from clive_local_tools.testnet_block_log.constants import CREATOR_ACCOUNT, WATCHED_ACCOUNTS, WORKING_ACCOUNT

if TYPE_CHECKING:
    from collections.abc import Sequence


def init_argparse(args: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clive testnet configurator")

    add = parser.add_argument

    add(
        "-p",
        "--perform-onboarding",
        nargs="?",
        type=bool,
        const=True,
        default=False,
        help="if not set, pregenerated profile will be used, otherwise clive onboarding will be launched",
    )
    add(
        "-n",
        "--no-tui",
        nargs="?",
        type=bool,
        const=True,
        default=False,
        help="if not set, TUI will will be launched, otherwise only testnet will be configured",
    )

    return parser.parse_args(args)


def prepare_node() -> tt.RawNode:
    config_lines = get_config().write_to_lines()
    block_log = get_block_log()
    alternate_chain_spec_path = get_alternate_chain_spec_path()
    node = tt.RawNode()
    node.config.load_from_lines(config_lines)
    node.config.webserver_http_endpoint = "0.0.0.0:8090"
    arguments = ["--alternate-chain-spec", str(alternate_chain_spec_path)]
    node.run(replay_from=block_log, arguments=arguments)

    return node


async def prepare_profile(node: tt.RawNode) -> None:
    tt.logger.info("Configuring ProfileData for clive")
    settings["secrets.node_address"] = node.http_endpoint.as_string()
    settings["node.chain_id"] = TESTNET_CHAIN_ID

    ProfileData(
        WORKING_ACCOUNT.name,
        working_account=WorkingAccount(name=WORKING_ACCOUNT.name),
        watched_accounts=[WatchedAccount(acc.name) for acc in WATCHED_ACCOUNTS],
    ).save()

    async with World(WORKING_ACCOUNT.name) as world:
        password = await CreateWallet(
            app_state=world.app_state,
            beekeeper=world.beekeeper,
            wallet=WORKING_ACCOUNT.name,
            password=WORKING_ACCOUNT.name,
        ).execute_with_result()

        tt.logger.info(f"password for {WORKING_ACCOUNT.name} is: `{password}`")
        world.profile_data.working_account.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT.private_key, alias=f"{WORKING_ACCOUNT.name}_key")
        )
        await world.commands.sync_data_with_beekeeper()


def create_proposal(wallet: tt.Wallet) -> None:
    proposal_authors = ["initminer", "alice", "bob", "john"]

    for discriminator, author in enumerate(proposal_authors, start=1):
        wallet.api.post_comment(
            author=author,
            permlink=f"test-permlink-{discriminator}",
            parent_author="",
            parent_permlink=f"test-parent-{discriminator}",
            title=f"test-title-{discriminator}",
            body=f"test-body-{discriminator}",
            json="{}",
        )

        wallet.api.create_proposal(
            creator=author,
            receiver="alice",
            start_date=tt.Time.now(),
            end_date=tt.Time.from_now(weeks=discriminator),
            daily_pay=tt.Asset.Tbd(discriminator).as_nai(),
            subject=f"test-subject-{discriminator}",
            permlink=f"test-permlink-{discriminator}",
        )


def send_test_transfer_from_working_account(wallet: tt.Wallet) -> None:
    wallet.api.transfer(WORKING_ACCOUNT.name, CREATOR_ACCOUNT.name, tt.Asset.Test(1).as_nai(), memo="memo")


def print_working_account_keys() -> None:
    tt.logger.info(f"{WORKING_ACCOUNT.name} public key: {WORKING_ACCOUNT.public_key}")
    tt.logger.info(f"{WORKING_ACCOUNT.name} private key: {WORKING_ACCOUNT.private_key}")


async def launch_clive() -> None:
    tt.logger.info("Attempting to start a clive interactive mode - exit to finish")
    await clive_main()


def serve_forever() -> None:
    tt.logger.info("Serving forever... press Ctrl+C to exit")

    while True:
        time.sleep(1)


async def main() -> None:
    args = init_argparse(sys.argv[1:])
    enable_clive_onboarding = args.perform_onboarding
    disable_tui = args.no_tui

    node = prepare_node()
    print_working_account_keys()

    if not enable_clive_onboarding:
        shutil.rmtree(settings.data_path, ignore_errors=True)
        await prepare_profile(node)

    if disable_tui:
        serve_forever()
    else:
        await launch_clive()


if __name__ == "__main__":
    asyncio.run(main())
