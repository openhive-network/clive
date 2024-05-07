from __future__ import annotations

import re
from typing import TYPE_CHECKING

import test_tools as tt

if TYPE_CHECKING:
    from .cli_tester import CLITester


def get_account_creation_fee(cli_tester: CLITester) -> tt.Asset.HiveT:
    result = cli_tester.show_chain()
    output = result.output
    account_creation_fee_message = "account creation fee"
    lines = [line for line in output.split("\n") if account_creation_fee_message in line]
    match = re.search(r"\d+\.?\d*", lines[0])
    assert match is not None, f"Coluldn't get account creation fee from command `clive show chain` output:\n{output}"
    fee = tt.Asset.Test(match.group(0))
    tt.logger.debug(f"{account_creation_fee_message} is {fee.pretty_amount()}")
    return fee
