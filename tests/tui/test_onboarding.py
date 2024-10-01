from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.ui.app import Clive
from clive.__private.ui.onboarding.create_profile_form import CreateProfileForm
from clive.__private.ui.onboarding.new_key_alias_form import NewKeyAliasForm
from clive.__private.ui.onboarding.onboarding import OnboardingFinishScreen, OnboardingWelcomeScreen
from clive.__private.ui.onboarding.set_account import SetAccount
from clive.__private.ui.onboarding.set_account.set_account import WorkingAccountCheckbox
from clive.__private.ui.screens.config import Config
from clive.__private.ui.screens.config.manage_key_aliases.manage_key_aliases import KeyAliasRow, ManageKeyAliases
from clive.__private.ui.screens.dashboard import Dashboard
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.private_key_input import PrivateKeyInput
from clive.__private.ui.widgets.inputs.public_key_alias_input import PublicKeyAliasInput
from clive.__private.ui.widgets.inputs.repeat_password_input import RepeatPasswordInput
from clive.__private.ui.widgets.inputs.set_password_input import SetPasswordInput
from clive.__private.ui.widgets.inputs.set_profile_name_input import SetProfileNameInput
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA
from clive_local_tools.tui.checkers import (
    assert_is_clive_composed_input_focused,
    assert_is_dashboard,
    assert_is_focused,
    assert_is_screen_active,
)
from clive_local_tools.tui.clive_quit import clive_quit
from clive_local_tools.tui.textual_helpers import (
    focus_next,
    press_and_wait_for_screen,
    write_text,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clive_local_tools.tui.types import ClivePilot
    from tests.tui.conftest import NodeWithWallet


PROFILE_NAME: Final[str] = "master"
PROFILE_PASSWORD: Final[str] = PROFILE_NAME + PROFILE_NAME
ACCOUNT_NAME: Final[str] = WORKING_ACCOUNT_DATA.account.name
PRIVATE_KEY: Final[str] = WORKING_ACCOUNT_DATA.account.private_key
KEY_ALIAS_NAME: Final[str] = "master@active"


@pytest.fixture
async def prepared_tui_on_onboarding(
    node_with_wallet: NodeWithWallet,  # noqa: ARG001
) -> AsyncIterator[ClivePilot]:
    async with Clive().run_test() as pilot:
        yield pilot

        await clive_quit(pilot)


async def onboarding_until_set_account(
    pilot: ClivePilot, profile_name: str, profile_password: str, account_name: str
) -> None:
    assert_is_screen_active(pilot, OnboardingWelcomeScreen)
    await press_and_wait_for_screen(pilot, "ctrl+n", CreateProfileForm)
    assert_is_clive_composed_input_focused(
        pilot, SetProfileNameInput, context="CreateProfileForm should have initial focus"
    )
    await write_text(pilot, profile_name)
    await focus_next(pilot)
    assert_is_clive_composed_input_focused(pilot, SetPasswordInput)
    await write_text(pilot, profile_password)
    await focus_next(pilot)
    assert_is_clive_composed_input_focused(pilot, RepeatPasswordInput)
    await write_text(pilot, profile_password)
    await press_and_wait_for_screen(pilot, "ctrl+n", SetAccount)
    assert_is_clive_composed_input_focused(pilot, AccountNameInput)
    await write_text(pilot, account_name)


async def onboarding_mark_account_as_watched(pilot: ClivePilot) -> None:
    assert_is_screen_active(pilot, SetAccount)
    assert_is_clive_composed_input_focused(pilot, AccountNameInput, context="SetAccount should have initial focus")
    await focus_next(pilot)
    assert_is_focused(pilot, WorkingAccountCheckbox)
    await pilot.press("space")  # Uncheck 'Working account?'
    assert (
        pilot.app.screen.query_exactly_one(WorkingAccountCheckbox).value is False
    ), "Expected 'Working account?' to be unchecked!"


async def onboarding_set_key_and_alias_name(pilot: ClivePilot, alias_name: str, private_key: str) -> None:
    assert_is_screen_active(pilot, NewKeyAliasForm)
    assert_is_clive_composed_input_focused(
        pilot, PublicKeyAliasInput, context="KeyAliasForm screen should have initial focus"
    )
    await write_text(pilot, alias_name)
    await focus_next(pilot)
    assert_is_clive_composed_input_focused(pilot, PrivateKeyInput)
    await write_text(pilot, private_key)


async def onboarding_finish(pilot: ClivePilot) -> None:
    await press_and_wait_for_screen(pilot, "ctrl+n", OnboardingFinishScreen)
    await press_and_wait_for_screen(pilot, "enter", Dashboard)
    assert_is_dashboard(pilot)


async def assert_tui_key_alias_exists(pilot: ClivePilot) -> None:
    assert_is_dashboard(pilot)
    await press_and_wait_for_screen(pilot, "f6", Config)
    await focus_next(pilot)
    await press_and_wait_for_screen(pilot, "enter", ManageKeyAliases)
    key_aliases = pilot.app.screen.query(KeyAliasRow)
    assert len(key_aliases) == 1, f"Expected 1 key-alias, current count is: {len(key_aliases)}"


def assert_working_account(pilot: ClivePilot, name: str) -> None:
    assert pilot.app.world.profile.accounts.has_working_account, "Expected working account to be set"
    assert pilot.app.world.profile.accounts.working.name == name, f"Expected working account to be {name}"


def assert_watched_accounts(pilot: ClivePilot, *names: str) -> None:
    watched_account_names = [account.name for account in pilot.app.world.profile.accounts.watched]
    assert watched_account_names == list(names), f"Expected watched accounts to be {list(names)}"


def assert_no_watched_accounts(pilot: ClivePilot) -> None:
    assert not pilot.app.world.profile.accounts.watched, "Expected no watched accounts"


def assert_no_working_account(pilot: ClivePilot) -> None:
    assert not pilot.app.world.profile.accounts.has_working_account, "Expected no working account"


async def test_onboarding_watched_account_creation(prepared_tui_on_onboarding: ClivePilot) -> None:
    # ARRANGE
    pilot = prepared_tui_on_onboarding

    # ACT
    await onboarding_until_set_account(pilot, PROFILE_NAME, PROFILE_PASSWORD, ACCOUNT_NAME)
    await onboarding_mark_account_as_watched(pilot)
    await onboarding_finish(pilot)

    # ASSERT
    assert_no_working_account(pilot)
    assert_watched_accounts(pilot, ACCOUNT_NAME)


async def test_onboarding_working_account_creation(prepared_tui_on_onboarding: ClivePilot) -> None:
    # ARRANGE
    pilot = prepared_tui_on_onboarding

    # ACT
    await onboarding_until_set_account(pilot, PROFILE_NAME, PROFILE_PASSWORD, ACCOUNT_NAME)
    await press_and_wait_for_screen(pilot, "ctrl+n", NewKeyAliasForm)
    await onboarding_set_key_and_alias_name(pilot, KEY_ALIAS_NAME, PRIVATE_KEY)
    await onboarding_finish(pilot)

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
    await onboarding_finish(pilot)

    # ASSERT
    assert_working_account(pilot, ACCOUNT_NAME)
    assert_no_watched_accounts(pilot)
