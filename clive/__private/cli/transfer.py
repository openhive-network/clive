from typing import Final

import typer

from clive.__private.cli.commands.transfer import Transfer
from clive.__private.cli.common.operation_common import OperationCommon

HELP: Final[str] = """
Transfer some funds to another account.
"""  # fmt: skip

transfer = typer.Typer(
    help=HELP,
    epilog='Example: [yellow]clive transfer --sign mykeyalias --to clive --amount "1.000 HBD" --memo "For coffee!"[/]',
)


@transfer.callback(invoke_without_command=True)
@OperationCommon.decorator
def _main(
    ctx: typer.Context,
    to: str = typer.Option(..., help="The account to transfer to.", show_default=False),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)", show_default=False),
    memo: str = typer.Option("", help="The memo to attach to the transfer."),
) -> None:
    common = OperationCommon(**ctx.params)
    Transfer(
        world=common.world,
        sign=common.sign,
        save_file=common.save_file,
        broadcast=common.broadcast,
        to=to,
        amount=amount,
        memo=memo,
    ).run()
