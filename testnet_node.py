from __future__ import annotations

import argparse
import asyncio
import shutil
import sys
import time
from typing import TYPE_CHECKING

import test_tools as tt
from beekeepy import interfaces as bki

from clive.__private.before_launch import prepare_before_launch
from clive.__private.core.constants.setting_identifiers import NODE_CHAIN_ID, SECRETS_NODE_ADDRESS
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.world import World
from clive.__private.run_tui import run_tui
from clive.__private.settings import get_settings, safe_settings
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    TESTNET_CHAIN_ID,
    WORKING_ACCOUNT_KEY_ALIAS,
)
from clive_local_tools.testnet_block_log import run_node
from clive_local_tools.testnet_block_log.constants import (
    ALT_WORKING_ACCOUNT1_DATA,
    ALT_WORKING_ACCOUNT1_NAME,
    KNOWN_ACCOUNTS,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


def init_argparse(args: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clive testnet configurator")

    add = parser.add_argument

    add(
        "-p",
        "--prepare-profiles",
        action="store_true",
        default=False,
        help="When set, pregenerated profiles will be created. Otherwise clive create_profile will be launched.",
    )
    add(
        "-t",
        "--tui",
        action="store_true",
        default=False,
        help="When set, TUI will be launched. Otherwise only testnet node will be configured and launched.",
    )

    return parser.parse_args(args)


def prepare_node() -> tt.RawNode:
    return run_node(webserver_http_endpoint=bki.HttpUrl.factory(port=8090))


async def prepare_profiles(node: tt.RawNode) -> None:
    tt.logger.info("Configuring profiles for clive")
    settings = get_settings()
    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())
    settings.set(NODE_CHAIN_ID, TESTNET_CHAIN_ID)

    await _create_profile_with_wallet(
        profile_name=WORKING_ACCOUNT_NAME,
        working_account_name=WORKING_ACCOUNT_NAME,
        known_accounts=KNOWN_ACCOUNTS,
        private_key=WORKING_ACCOUNT_DATA.account.private_key,
        key_alias=WORKING_ACCOUNT_KEY_ALIAS,
    )
    await _create_profile_with_wallet(
        profile_name=ALT_WORKING_ACCOUNT1_NAME,
        working_account_name=ALT_WORKING_ACCOUNT1_NAME,
        known_accounts=KNOWN_ACCOUNTS,
        private_key=ALT_WORKING_ACCOUNT1_DATA.account.private_key,
        key_alias=ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    )


async def _create_profile_with_wallet(
    profile_name: str, working_account_name: str, known_accounts: Iterable[str], private_key: str, key_alias: str
) -> None:
    async with World() as world_cm:
        password = profile_name * 2
        await world_cm.create_new_profile_with_wallets(
            profile_name,
            password,
            working_account_name,
            known_accounts=known_accounts,
        )
        tt.logger.info(f"password for profile `{profile_name}` is: `{password}`")
        world_cm.profile.keys.add_to_import(PrivateKeyAliased(value=private_key, alias=key_alias))
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


def launch_tui() -> None:
    tt.logger.info("Attempting to start a clive interactive mode - exit to finish")
    run_tui()


def serve_forever() -> None:
    tt.logger.info("Serving forever... press Ctrl+C to exit")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tt.logger.info("Exiting...")
        return


def cleanup_clive_data() -> None:
    excluded = [safe_settings.select_file_root_path]
    data_path = safe_settings.data_path

    for child in data_path.iterdir():
        if child not in excluded:
            shutil.rmtree(child, ignore_errors=True)


async def prepare(*, recreate_profiles: bool) -> tt.RawNode:
    prepare_before_launch(enable_textual_logger=False, enable_stream_handlers=True)
    node = prepare_node()
    print_working_account_keys()

    if recreate_profiles:
        cleanup_clive_data()
        prepare_before_launch(enable_textual_logger=False, enable_stream_handlers=True)
        await prepare_profiles(node)

    return node


def main() -> None:
    args = init_argparse(sys.argv[1:])
    should_prepare_profiles = args.prepare_profiles
    should_launch_tui = args.tui

    node = asyncio.run(prepare(recreate_profiles=should_prepare_profiles))

    if should_launch_tui:
        launch_tui()
    else:
        serve_forever()

    node.close()


if __name__ == "__main__":
    main()
