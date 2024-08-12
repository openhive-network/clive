from __future__ import annotations

import argparse
import asyncio
import shutil
import sys
import time
from typing import TYPE_CHECKING

import test_tools as tt

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.constants.setting_identifiers import NODE_CHAIN_ID, SECRETS_NODE_ADDRESS
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.settings import safe_settings, settings
from clive.main import _main as clive_main
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    TESTNET_CHAIN_ID,
    WORKING_ACCOUNT_KEY_ALIAS,
)
from clive_local_tools.testnet_block_log import run_node
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    WATCHED_ACCOUNTS_NAMES,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

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
    # TODO: time_offset/use_faketime option should be used there but faketime is not available in the embedded_testnet
    #  docker image yet
    return run_node(webserver_http_endpoint="0.0.0.0:8090")


async def prepare_profile(node: tt.RawNode) -> None:
    tt.logger.info("Configuring ProfileData for clive")
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    settings.set(NODE_CHAIN_ID, TESTNET_CHAIN_ID)

    _create_profile_data(
        profile_name=WORKING_ACCOUNT_NAME,
        working_account_name=WORKING_ACCOUNT_NAME,
        watched_accounts_names=WATCHED_ACCOUNTS_NAMES,
    )
    _create_profile_data(
        profile_name=ALT_WORKING_ACCOUNT1_NAME,
        working_account_name=ALT_WORKING_ACCOUNT1_NAME,
        watched_accounts_names=WATCHED_ACCOUNTS_NAMES,
    )
    await _create_wallet(
        working_account_name=WORKING_ACCOUNT_NAME,
        private_key=WORKING_ACCOUNT_DATA.account.private_key,
        key_alias=WORKING_ACCOUNT_KEY_ALIAS,
    )
    await _create_wallet(
        working_account_name=ALT_WORKING_ACCOUNT1_NAME,
        private_key=ALT_WORKING_ACCOUNT1_DATA.account.private_key,
        key_alias=ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    )


def _create_profile_data(profile_name: str, working_account_name: str, watched_accounts_names: list[str]) -> None:
    ProfileData(
        profile_name,
        working_account=WorkingAccount(name=working_account_name),
        watched_accounts=[WatchedAccount(name) for name in watched_accounts_names],
    ).save()


async def _create_wallet(working_account_name: str, private_key: str, key_alias: str) -> None:
    async with World(working_account_name) as world_cm:
        password = await CreateWallet(
            app_state=world_cm.app_state,
            beekeeper=world_cm.beekeeper,
            wallet=working_account_name,
            password=working_account_name,
        ).execute_with_result()

        tt.logger.info(f"password for profile `{working_account_name}` is: `{password}`")
        world_cm.profile_data.keys.add_to_import(PrivateKeyAliased(value=private_key, alias=key_alias))
        await world_cm.commands.sync_data_with_beekeeper()


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


def print_working_account_keys() -> None:
    tt.logger.info(f"{WORKING_ACCOUNT_NAME} public key: {WORKING_ACCOUNT_DATA.account.public_key}")
    tt.logger.info(f"{WORKING_ACCOUNT_NAME} private key: {WORKING_ACCOUNT_DATA.account.private_key}")


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
        shutil.rmtree(safe_settings.data_path, ignore_errors=True)
        await prepare_profile(node)

    if disable_tui:
        serve_forever()
    else:
        await launch_clive()


if __name__ == "__main__":
    asyncio.run(main())
