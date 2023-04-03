from __future__ import annotations

from typing import Final, Optional

import typer

from clive.__private.cli import common

HELP: Final[str] = """
Transfer some funds to another account.
"""  # fmt: skip

transfer = typer.Typer(
    help=HELP,
    epilog='Example: [yellow]clive transfer --from clive --to clive --amount "1.000 HBD" --memo "For coffee!"[/]',
)


@transfer.callback(invoke_without_command=True)
def _main(
    from_: str = typer.Option(..., "--from", help="The account to transfer from."),
    to: str = typer.Option(..., help="The account to transfer to."),
    amount: str = typer.Option(..., help="The amount to transfer. (e.g. 2.500 HIVE)"),
    memo: Optional[str] = typer.Option(None, help="The memo to attach to the transfer."),
    broadcast: bool = common.Broadcast,
    sign: Optional[str] = common.Sign,
    profile: Optional[str] = common.Profile,
    password: Optional[str] = common.Password,
    save_file: Optional[str] = common.SaveFile,
) -> None:
    saved_args = locals()
    typer.echo(f"Transfer command invoked with params: {saved_args}")

    value, asset = amount.split(" ")

    from clive.__private.core.commands.transfer import Transfer

    Transfer.execute(from_=from_, to=to, amount=value, asset=asset.upper(), memo=memo)
