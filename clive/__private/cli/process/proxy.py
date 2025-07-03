from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

proxy = CliveTyper(name="proxy", help="Set, change or remove a proxy.")


@proxy.command(name="set")
async def process_proxy_set(
    account_name: str = options.account_name,
    proxy: str = typer.Option(..., help="Name of new proxy account."),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Set a proxy or change an existing proxy.

    Args:
        account_name: Name of the account to set the proxy for.
        proxy: Name of the new proxy account.
        sign: Optional signature for the operation.
        broadcast: Whether to broadcast the transaction.
        save_file: Optional file to save the transaction details.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_proxy_set import ProcessProxySet

    await ProcessProxySet(
        account_name=account_name,
        proxy=proxy,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    ).run()


@proxy.command(name="clear")
async def process_proxy_clear(
    account_name: str = options.account_name,
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Remove a proxy.

    Args:
        account_name: Name of the account to remove the proxy from.
        sign: Optional signature for the operation.
        broadcast: Whether to broadcast the transaction.
        save_file: Optional file to save the transaction details.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_proxy_clear import ProcessProxyClear

    await ProcessProxyClear(account_name=account_name, sign=sign, broadcast=broadcast, save_file=save_file).run()
