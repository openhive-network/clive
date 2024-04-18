from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.ui.app import Clive
from clive.__private.ui.config.config import Config
from clive.__private.ui.create_profile.create_profile import CreateProfileForm
from clive.__private.ui.dashboard.dashboard_active import DashboardActive
from clive.__private.ui.manage_key_aliases.manage_key_aliases import KeyAlias, ManageKeyAliases
from clive.__private.ui.manage_key_aliases.new_key_alias import NewKeyAliasForm
from clive.__private.ui.onboarding.onboarding import OnboardingFinishScreen, OnboardingWelcomeScreen
from clive.__private.ui.set_account.set_account import SetAccount
from clive.__private.ui.set_node_address.set_node_address import SetNodeAddressForm
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT
from clive_local_tools.tui.checkers import assert_is_screen_active
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    write_text,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import test_tools as tt

    from clive.__private.core.world import TextualWorld
    from clive_local_tools.tui.types import ClivePilot


USER: Final[str] = WORKING_ACCOUNT.name
PASS: Final[str] = USER + USER
PRIVATE_KEY = WORKING_ACCOUNT.private_key
ALT_USER: Final[str] = WATCHED_ACCOUNTS[1].name
ALT_PASS: Final[str] = ALT_USER + ALT_USER


@pytest.fixture()
def prepare_profile() -> None:
    pass


@pytest.fixture()
async def prepared_tui_on_onboarding(
    world: TextualWorld, _node_with_wallet: tuple[tt.RawNode, tt.Wallet]
) -> AsyncIterator[ClivePilot]:
    node, wallet = _node_with_wallet

    app = Clive.app_instance()
    Clive.world = world

    pilot: ClivePilot
    async with app.run_test() as pilot:
        yield pilot

        await clive_quit(pilot)


TESTDATA: Final[list[tuple[str, str, bool, str | None]]] = [
    (USER, PASS, True, PRIVATE_KEY),  # #138 p. 1
    (USER, PASS, True, None),  # #138 p. 2
    (ALT_USER, ALT_PASS, False, None),  # #138 p. 3
]


@pytest.mark.parametrize(("account_name", "password", "working_account", "private_key"), TESTDATA)
async def test_onboarding(
    prepared_tui_on_onboarding: ClivePilot,
    account_name: str,
    password: str,
    working_account: bool,
    private_key: str | None,
) -> None:
    """
    Issue #138.

    1. The user goes through the onboarding process and creates working account without adding a key and creates a profile.
    2. The user goes through the onboarding process and creates working account, adds a key and creates a profile.
    3. The user goes through the onboarding process, creates watched account and creates a profile.
    """
    pilot = prepared_tui_on_onboarding

    # ASSERT
    assert_is_screen_active(pilot, OnboardingWelcomeScreen)

    # ACT
    await press_and_wait_for_screen(pilot, "ctrl+n", CreateProfileForm)
    await write_text(pilot, account_name)
    await focus_next(pilot)  # 'Password' is focused
    await write_text(pilot, password)
    await focus_next(pilot)  # 'Repeat password' is focused
    await write_text(pilot, password)
    await press_and_wait_for_screen(pilot, "ctrl+n", SetNodeAddressForm)
    await press_and_wait_for_screen(pilot, "ctrl+n", SetAccount)
    await write_text(pilot, account_name)
    await focus_next(pilot)  # 'Known?' is focused
    await focus_next(pilot)  # 'Working account?' is focused
    if working_account:
        await press_and_wait_for_screen(pilot, "ctrl+n", NewKeyAliasForm)
        if private_key is not None:
            await focus_next(pilot)  # 'Private key' is focused
            await write_text(pilot, private_key)
        await press_and_wait_for_screen(pilot, "ctrl+n", OnboardingFinishScreen)
    else:
        await pilot.press("space")
        await press_and_wait_for_screen(pilot, "ctrl+n", OnboardingFinishScreen)

    # ACT & ASSERT
    await press_and_wait_for_screen(pilot, "f10", DashboardActive)

    if private_key is not None:  # In case of private_key passed, check if exists in Config->Manage key aliases
        # ACT
        await press_and_wait_for_screen(pilot, "f9", Config)
        await focus_next(pilot)  # 'Manage key aliases' is focused
        await press_and_wait_for_screen(pilot, "enter", ManageKeyAliases)

        # ASSERT
        # Check if key-alias exists
        key_aliases = pilot.app.screen.query(KeyAlias)
        assert len(key_aliases) == 1, f"Expected 1 key-alias, current count is: {len(key_aliases)}"
