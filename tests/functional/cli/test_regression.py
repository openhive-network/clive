from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.cli.exceptions import CLITestCommandError

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester
    from clive_local_tools.types import EnvContextFactory


async def test_configure_node_set_address_regression_issue_345(
    cli_tester: CLITester, node_address_env_context_factory: EnvContextFactory
) -> None:
    """Regression test for issue https://gitlab.syncad.com/hive/clive/-/issues/345."""
    # ARRANGE
    expected_node_address: Final[str] = "http://-h"
    expected_error: Final[str] = f"Could not communicate with (seems to be unavailable): {expected_node_address}"

    # ACT
    cli_tester.configure_node_set(node_address=expected_node_address)

    # ASSERT

    # required to unset SECRETS_NODE_ADDRESS which is used in other tests and overrides the value set via this test
    with node_address_env_context_factory(None):
        await cli_tester.world.load_profile_based_on_beekepeer()  # reload profile
        actual_node_address = cli_tester.world.profile.node_address
        assert str(actual_node_address) == expected_node_address, "The node address was not set correctly."

        # assert that running a command will raise a correct error
        # because previously no command could be run due to an issue with parsing the node address from the
        # saved profile, and it resulted in unhandled exception traceback
        with pytest.raises(CLITestCommandError) as err:
            cli_tester.show_chain()

    # there is an issue with logs being visible in the output, so we can't use exact match
    assert expected_error in str(err.value), "The error message is not as expected."
