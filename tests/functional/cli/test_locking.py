from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from typing import AsyncGenerator

    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import EnvContextFactory

MESSAGE_NO_REMOTE_ADDRESS: Final[str] = "Beekeeper remote address is not set"


@pytest.fixture
async def cli_tester_without_remote_address(
    beekeeper_remote_address_env_context_factory: EnvContextFactory,
    cli_tester: CLITester,
) -> AsyncGenerator[CLITester]:
    with beekeeper_remote_address_env_context_factory(None):
        yield cli_tester


async def test_negative_lock_without_remote_address(cli_tester_without_remote_address: CLITester) -> None:
    # ARRANGE

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=MESSAGE_NO_REMOTE_ADDRESS):
        cli_tester_without_remote_address.lock()


async def test_negative_unlock_without_remote_address(cli_tester_without_remote_address: CLITester) -> None:
    # ARRANGE

    # ACT
    # ASSERT
    with pytest.raises(CLITestCommandError, match=MESSAGE_NO_REMOTE_ADDRESS):
        cli_tester_without_remote_address.unlock(
            profile_name=WORKING_ACCOUNT_NAME, password_stdin=WORKING_ACCOUNT_PASSWORD
        )
