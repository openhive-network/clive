from __future__ import annotations

from contextlib import AsyncExitStack
from functools import partialmethod
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.accounts.accounts import WatchedAccount, WorkingAccount
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.create_profile_encryption_wallet import CreateProfileEncryptionWallet
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.constants.setting_identifiers import SECRETS_NODE_ADDRESS
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.keys.keys import PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.core.world import World
from clive.__private.settings import settings
from clive.__private.ui.app import Clive
from clive.__private.ui.onboarding.unlock_screen import UnlockScreen
from clive.__private.ui.screens.dashboard import Dashboard
from clive_local_tools.data.constants import (
    BEEKEEPER_SESSION_TOKEN_ENV_NAME,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA, run_node
from clive_local_tools.tui.checkers import assert_is_screen_active
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.constants import TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT
from clive_local_tools.tui.textual_helpers import wait_for_screen
from clive_local_tools.tui.workaround_incompatibility_with_fixtures import event_loop  # noqa: F401

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clive_local_tools.tui.types import ClivePilot
    from clive_local_tools.types import BeekeeperSessionTokenEnvContextFactory

    NodeWithWallet = tuple[tt.RawNode, tt.Wallet]
    PreparedTuiEnv = tuple[tt.RawNode, tt.Wallet, ClivePilot]


@pytest.fixture(autouse=True)
def _patch_notification_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Clive, "notify", partialmethod(Clive.notify, timeout=TUI_TESTS_PATCHED_NOTIFICATION_TIMEOUT))


@pytest.fixture
async def prepare_profile(env_variable_context: BeekeeperSessionTokenEnvContextFactory) -> Profile:
    async with Beekeeper() as beekeeper_cm:
        profile = Profile(
            WORKING_ACCOUNT_DATA.account.name,
            working_account=WorkingAccount(name=WORKING_ACCOUNT_DATA.account.name),
            watched_accounts=[WatchedAccount(data.account.name) for data in WATCHED_ACCOUNTS_DATA],
        )
        await CreateProfileEncryptionWallet(
            beekeeper=beekeeper_cm, profile_name=profile.name, password=WORKING_ACCOUNT_PASSWORD
        ).execute_with_result()
        await CreateWallet(beekeeper=beekeeper_cm, wallet=profile.name, password=WORKING_ACCOUNT_PASSWORD).execute()
        encryption_service = await EncryptionService.from_beekeeper(beekeeper_cm)
        await profile.save(encryption_service)
        async with AsyncExitStack() as stack:
            stack.enter_context(env_variable_context(BEEKEEPER_SESSION_TOKEN_ENV_NAME, beekeeper_cm.token))
            world_cm = await stack.enter_async_context(World(beekeeper_remote_endpoint=beekeeper_cm.http_endpoint))
            private_key = PrivateKeyAliased(
                value=WORKING_ACCOUNT_DATA.account.private_key, alias=WORKING_ACCOUNT_KEY_ALIAS
            )
            world_cm.profile.keys.add_to_import(private_key)
            await world_cm.commands.sync_data_with_beekeeper()
        return profile


@pytest.fixture
def node_with_wallet() -> NodeWithWallet:
    node = run_node(use_faketime=True)

    wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
    wallet.api.import_key(node.config.private_key[0])
    wallet.api.import_key(WORKING_ACCOUNT_DATA.account.private_key)
    account = wallet.api.get_account(WORKING_ACCOUNT_DATA.account.name)
    tt.logger.debug(f"working account: {account}")

    settings.set(SECRETS_NODE_ADDRESS, node.http_endpoint.as_string())

    return node, wallet


@pytest.fixture
async def prepared_env(
    prepare_profile: Profile,  # noqa: ARG001
    node_with_wallet: NodeWithWallet,
) -> AsyncIterator[PreparedTuiEnv]:
    node, wallet = node_with_wallet
    async with Clive().run_test() as pilot:
        await wait_for_screen(pilot, UnlockScreen)
        assert_is_screen_active(pilot, UnlockScreen)

        yield node, wallet, pilot

        await clive_quit(pilot)


@pytest.fixture
async def prepared_tui_on_dashboard(prepared_env: PreparedTuiEnv, prepare_profile: Profile) -> PreparedTuiEnv:
    node, wallet, pilot = prepared_env

    await pilot.app.world.commands.unlock(
        profile_name=prepare_profile.name, password=WORKING_ACCOUNT_PASSWORD, permanent=True
    )
    encryption_service = await EncryptionService.from_beekeeper(pilot.app.world.beekeeper)
    profile = await Profile.load(encryption_service)
    pilot.app.world.set_profile(profile)

    await pilot.app.push_screen(Dashboard())
    await wait_for_screen(pilot, Dashboard)
    assert_is_screen_active(pilot, Dashboard)
    return prepared_env
