from dataclasses import dataclass

import typer

from clive.__private.cli.common import options
from clive.__private.cli.common.common_options_base import CommonOptionsBase


@dataclass(kw_only=True)
class TransferCommonOptions(CommonOptionsBase):
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)", show_default=False)
    memo: str = typer.Option("", help="The memo to attach to the transfer.")
    from_account: str = options.from_account_name_option
