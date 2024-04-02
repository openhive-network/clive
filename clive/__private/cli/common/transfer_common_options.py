from dataclasses import dataclass

import typer

from clive.__private.cli.common import options
from clive.__private.cli.common.common_options_base import CommonOptionsBase
from clive.__private.cli.common.options import liquid_amount_option


@dataclass(kw_only=True)
class TransferCommonOptions(CommonOptionsBase):
    amount: str = liquid_amount_option
    memo: str = typer.Option("", help="The memo to attach to the transfer.")
    from_account: str = options.from_account_name_option
