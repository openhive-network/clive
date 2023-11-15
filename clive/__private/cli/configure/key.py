from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import WorldCommonOptions, options

key = CliveTyper(name="key", help="Manage your key(s).")


@key.command(name="add")
@WorldCommonOptions.decorator()
async def add_key(
    ctx: typer.Context,
    key_: str = typer.Option(
        ..., "--key", help="The key to import. This can be a path to a file or a key itself.", show_default=False
    ),
    alias: Optional[str] = typer.Option(
        None,
        help="The alias to use for the key. (If not given, calculated public key will be used)",
        show_default=False,
    ),
    password: str = options.password_option,
) -> None:
    """Import a key into the Beekeeper, and make it ready to use for Clive."""
    from clive.__private.cli.commands.configure.key import AddKey

    common = WorldCommonOptions(**ctx.params)
    await AddKey(**common.dict(), password=password, key_or_path=key_, alias=alias).run()
