from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME
from tests.functional.cli.process.escrow.conftest import get_future_datetime

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name  # bob
AGENT: Final[str] = WATCHED_ACCOUNTS_DATA[1].account.name  # timmy
HBD_AMOUNT: Final[tt.Asset.TbdT] = tt.Asset.Tbd(10)
HIVE_AMOUNT: Final[tt.Asset.TestT] = tt.Asset.Test(0)
FEE: Final[tt.Asset.TbdT] = tt.Asset.Tbd(1)


async def test_show_escrow(
    node: tt.RawNode,  # noqa: ARG001
    cli_tester: CLITester,
) -> None:
    """Test clive show escrow command."""
    # ARRANGE - create an escrow first
    ratification_deadline = get_future_datetime(1)
    escrow_expiration = get_future_datetime(7)
    escrow_id = 20

    cli_tester.process_escrow_transfer(
        from_=WORKING_ACCOUNT_NAME,
        to=RECEIVER,
        agent=AGENT,
        escrow_id=escrow_id,
        hbd_amount=HBD_AMOUNT,
        hive_amount=HIVE_AMOUNT,
        fee=FEE,
        ratification_deadline=ratification_deadline,
        escrow_expiration=escrow_expiration,
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    )

    # ACT
    result = cli_tester.show_escrow(account_name=WORKING_ACCOUNT_NAME)

    # ASSERT
    assert result.exit_code == 0
    # The output should contain the escrow table or escrow information
    output = result.output.lower()
    assert "escrow" in output or RECEIVER in result.output


async def test_show_escrow_empty(
    cli_tester: CLITester,
) -> None:
    """Test clive show escrow command when no escrows exist."""
    # ARRANGE - use an account that has no escrows
    account_with_no_escrows = WATCHED_ACCOUNTS_DATA[2].account.name  # john

    # ACT
    result = cli_tester.show_escrow(account_name=account_with_no_escrows)

    # ASSERT
    assert result.exit_code == 0
    # Should show a message about no escrows
    output = result.output.lower()
    assert "no escrow" in output or "has no" in output
