from dataclasses import dataclass
from typing import Optional

import typer

from clive.__private.cli.common.common_options_base import CommonOptionsBase
from clive.__private.cli.common.parameters import options


@dataclass(kw_only=True)
class OperationCommonOptions(CommonOptionsBase):
    profile_name: str = options.profile_name
    password: Optional[str] = options.password_optional
    sign: Optional[str] = typer.Option(None, help="Key alias to sign the transaction with.", show_default=False)
    beekeeper_remote: Optional[str] = options.beekeeper_remote
    broadcast: bool = typer.Option(default=True, help="Whether broadcast the transaction. (i.e. dry-run)")
    save_file: Optional[str] = typer.Option(
        None,
        help="The file to save the transaction to (format is determined by file extension - .bin or .json).",
        show_default=False,
    )
