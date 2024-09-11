from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.setting_identifiers import BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import clive_prefixed_envvar, settings
from clive_local_tools.cli.checkers import assert_no_exit_code_error

if TYPE_CHECKING:
    import clive
    from clive_local_tools.cli.cli_tester import CLITester
import os

import test_tools as tt


async def test_transfer_with_beekeeper_session_token(world: clive.World, cli_tester: CLITester) -> None:
    """Check if clive process transfer requires --password when CLIVE_BEEKEEPER__SESSION_TOKEN is set."""
    async with world as _:
        # ARRANGE
        env_var = clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)
        await world.beekeeper.api.unlock(wallet_name="alice", password="alice")
        os.environ[env_var] = world.beekeeper.token
        settings.reload()

        # ACT
        result = cli_tester.process_transfer(from_="alice", amount=tt.Asset.Hive(1), to="bob", sign="alice_key")
        del os.environ[env_var]

        # ASSERT
        assert_no_exit_code_error(result)
