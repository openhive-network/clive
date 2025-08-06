from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options

proxy = CliveTyper(name="proxy", help="Set, change or remove a proxy.")


@proxy.command(name="set")
async def process_proxy_set(  # noqa: PLR0913
    account_name: str = options.account_name,
    proxy: str = typer.Option(..., help="Name of new proxy account."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Set a proxy or change an existing proxy."""
    from clive.__private.cli.commands.process.process_proxy_set import ProcessProxySet  # noqa: PLC0415

    await ProcessProxySet(
        account_name=account_name,
        proxy=proxy,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@proxy.command(name="clear")
async def process_proxy_clear(
    account_name: str = options.account_name,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Remove a proxy."""
    from clive.__private.cli.commands.process.process_proxy_clear import ProcessProxyClear  # noqa: PLC0415

    await ProcessProxyClear(
        account_name=account_name, sign_with=sign_with, broadcast=broadcast, save_file=save_file, autosign=autosign
    ).run()
