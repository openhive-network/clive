from dataclasses import dataclass
from functools import partial
from typing import Optional

import typer

from clive.__private.cli.common.parameters import modified_param, options
from clive.__private.cli.common.parameters.groups.parameter_group import ParameterGroup
from clive.__private.core.constants.cli import OPERATION_COMMON_OPTIONS_PANEL_TITLE

operation_common_option = partial(modified_param, rich_help_panel=OPERATION_COMMON_OPTIONS_PANEL_TITLE)


@dataclass(kw_only=True)
class OperationOptionsGroup(ParameterGroup):
    sign: Optional[str] = operation_common_option(
        typer.Option(None, help="Key alias to sign the transaction with.", show_default=False)
    )
    beekeeper_remote: Optional[str] = operation_common_option(options.beekeeper_remote)
    broadcast: bool = operation_common_option(
        typer.Option(default=True, help="Whether broadcast the transaction. (i.e. dry-run)")
    )
    save_file: Optional[str] = operation_common_option(
        typer.Option(
            None,
            help="The file to save the transaction to (format is determined by file extension - .bin or .json).",
            show_default=False,
        )
    )
