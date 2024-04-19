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
from clive.__private.ui.set_account.set_account import SetAccount, WorkingAccountCheckbox
from clive.__private.ui.set_node_address.set_node_address import SetNodeAddressForm
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.public_key_alias_input import PublicKeyAliasInput
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT
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

PROFILE_NAME: Final[str] = "master"
PROFILE_PASSWORD: Final[str] = PROFILE_NAME + PROFILE_NAME
ACCOUNT_NAME: Final[str] = WORKING_ACCOUNT.name
PRIVATE_KEY: Final[str] = WORKING_ACCOUNT.private_key


@pytest.fixture()
async def prepare_profile() -> None:
    """Skip profile creation so CLive will enter onboarding."""


@pytest.fixture()
async def prepared_tui_on_onboarding(
    world: TextualWorld, _node_with_wallet: tuple[tt.RawNode, tt.Wallet]
) -> AsyncIterator[ClivePilot]:
    app = Clive.app_instance()
    Clive.world = world

    pilot: ClivePilot
    async with app.run_test() as pilot:
        yield pilot

        await clive_quit(pilot)


async def onboarding_until_set_account(
    pilot: ClivePilot, profile_name: str, profile_password: str, account_name: str
) -> None:
    assert_is_screen_active(pilot, OnboardingWelcomeScreen)
    await press_and_wait_for_screen(pilot, "ctrl+n", CreateProfileForm)
    await write_text(pilot, profile_name)
    await focus_next(pilot)  # 'Password' is focused
    await write_text(pilot, profile_password)
    await focus_next(pilot)  # 'Repeat password' is focused
    await write_text(pilot, profile_password)
    await press_and_wait_for_screen(pilot, "ctrl+n", SetNodeAddressForm)
    await press_and_wait_for_screen(pilot, "ctrl+n", SetAccount)
    await write_text(pilot, account_name)


async def onboarding_mark_account_as_watched(pilot: ClivePilot) -> None:
    assert_is_screen_active(pilot, SetAccount)
    assert pilot.app.query_one(
        AccountNameInput
    ).input.has_focus, "Set account should have initial focus"  # TODO: create assert_is_input_focused?
    await focus_next(pilot)  # 'Known?' is focused
    await focus_next(pilot)  # 'Working account?' is focused
    await pilot.press("space")  # Uncheck 'Working account?'
    assert (
        pilot.app.screen.query_one(WorkingAccountCheckbox).value is False
    ), "Expected 'Working account?' to be unchecked!"


async def onboarding_set_key(pilot: ClivePilot, private_key: str) -> None:
    assert_is_screen_active(pilot, NewKeyAliasForm)
    assert pilot.app.screen.query_one(
        PublicKeyAliasInput
    ).input.has_focus, "KeyAliasForm screen should have initial focus"  # TODO: create assert_is_input_focused?
    await focus_next(pilot)  # 'Private key' is focused
    await write_text(pilot, private_key)


async def assert_tui_key_alias_exists(pilot: ClivePilot) -> None:
    await press_and_wait_for_screen(pilot, "f9", Config)
    await focus_next(pilot)
    await press_and_wait_for_screen(pilot, "enter", ManageKeyAliases)
    key_aliases = pilot.app.screen.query(KeyAlias)
    assert len(key_aliases) == 1, f"Expected 1 key-alias, current count is: {len(key_aliases)}"


def assert_working_account(pilot: ClivePilot, name: str) -> None:
    assert pilot.app.world.profile_data.is_working_account_set(), "Expected working account to be set"
    assert pilot.app.world.profile_data.working_account.name == name, f"Expected working account to be {name}"


def assert_watched_accounts(pilot: ClivePilot, *names: str) -> None:
    watched_account_names = [account.name for account in pilot.app.world.profile_data.watched_accounts]
    assert watched_account_names == list(names), f"Expected watched accounts to be {list(names)}"


def assert_no_watched_accounts(pilot: ClivePilot) -> None:
    assert not pilot.app.world.profile_data.watched_accounts, "Expected no watched accounts"


def assert_no_working_account(pilot: ClivePilot) -> None:
    assert not pilot.app.world.profile_data.is_working_account_set(), "Expected no working account"


async def test_onboarding_watched_account_creation(prepared_tui_on_onboarding: ClivePilot) -> None:
    # ARRANGE
    pilot = prepared_tui_on_onboarding

    # ACT
    await onboarding_until_set_account(pilot, PROFILE_NAME, PROFILE_PASSWORD, ACCOUNT_NAME)
    await onboarding_mark_account_as_watched(pilot)
    await press_and_wait_for_screen(pilot, "ctrl+n", OnboardingFinishScreen)
    await press_and_wait_for_screen(pilot, "f10", DashboardActive)

    # ASSERT
    assert_no_working_account(pilot)
    assert_watched_accounts(pilot, ACCOUNT_NAME)


async def test_onboarding_working_account_creation(prepared_tui_on_onboarding: ClivePilot) -> None:
    # ARRANGE
    pilot = prepared_tui_on_onboarding

    # ACT
    await onboarding_until_set_account(pilot, PROFILE_NAME, PROFILE_PASSWORD, ACCOUNT_NAME)
    await press_and_wait_for_screen(pilot, "ctrl+n", NewKeyAliasForm)
    await onboarding_set_key(pilot, PRIVATE_KEY)
    await press_and_wait_for_screen(pilot, "ctrl+n", OnboardingFinishScreen)
    await press_and_wait_for_screen(pilot, "f10", DashboardActive)

    # ASSERT
    assert_working_account(pilot, ACCOUNT_NAME)
    assert_no_watched_accounts(pilot)
    await assert_tui_key_alias_exists(pilot)


async def test_onboarding_working_account_creation_no_key(prepared_tui_on_onboarding: ClivePilot) -> None:
    # ARRANGE
    pilot = prepared_tui_on_onboarding

    # ACT
    await onboarding_until_set_account(pilot, PROFILE_NAME, PROFILE_PASSWORD, ACCOUNT_NAME)
    await press_and_wait_for_screen(pilot, "ctrl+n", NewKeyAliasForm)
    await press_and_wait_for_screen(pilot, "ctrl+n", OnboardingFinishScreen)
    await press_and_wait_for_screen(pilot, "f10", DashboardActive)

    # ASSERT
    assert_working_account(pilot, ACCOUNT_NAME)
    assert_no_watched_accounts(pilot)
