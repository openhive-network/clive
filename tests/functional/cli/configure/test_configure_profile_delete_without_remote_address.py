from __future__ import annotations

from typing import TYPE_CHECKING

import beekeepy as bk
import beekeepy.exceptions as bke
import pytest

from clive.__private.settings import safe_settings
from clive_local_tools.checkers.profile_checker import ProfileChecker
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from beekeepy import AsyncBeekeeper

    from clive_local_tools.cli.cli_tester import CLITester


@pytest.fixture
async def beekeeper_local() -> AsyncGenerator[AsyncBeekeeper]:
    """We need to handle error on double teardown of beekeeper."""
    with pytest.raises(
        bke.InvalidatedStateByClosingBeekeeperError
    ):  # we can use fixture beekeeper_local from conftest after issue #19 in beekeepey is resolved
        async with await bk.AsyncBeekeeper.factory(
            settings=safe_settings.beekeeper.settings_local_factory()
        ) as beekeeper_cm:
            yield beekeeper_cm


async def test_remove_profile_remote_address_not_set(
    beekeeper_local: AsyncBeekeeper, cli_tester_without_remote_address: CLITester
) -> None:
    # ARRANGE
    # profile can't be saved without beekeeper because there would be error during encryption
    cli_tester_without_remote_address.world.profile.skip_saving()
    # we call teardown here because configure_profile_delete runs second beekeeper when no remote_address is set
    beekeeper_local.teardown()

    # ACT
    cli_tester_without_remote_address.configure_profile_delete(profile_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    ProfileChecker.assert_profile_is_stored(WORKING_ACCOUNT_NAME, should_be_stored=False)
