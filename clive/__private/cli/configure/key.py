from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import WorldOptionsGroup
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

key = CliveTyper(name="key", help="Manage your key(s).")

_key_argument = typer.Argument(
    None,
    help=f"The key to import. This can be a path to a file or a key itself ({REQUIRED_AS_ARG_OR_OPTION}).",
    show_default=False,
)


_alias_argument = typer.Argument(
    None,
    help="The alias to use for the key. (If not given, calculated public key will be used).",
    show_default=False,
)


@key.command(name="add", param_groups=[WorldOptionsGroup])
async def add_key(
    ctx: typer.Context,  # noqa: ARG001
    key: Optional[str] = _key_argument,
    key_option: Optional[str] = argument_related_options.key,
    alias: Optional[str] = _alias_argument,
    alias_option: Optional[str] = argument_related_options.alias,
) -> None:
    """Import a key into the Beekeeper, and make it ready to use for Clive."""
    from clive.__private.cli.commands.configure.key import AddKey

    common = WorldOptionsGroup.get_instance()
    await AddKey(
        **common.as_dict(),
        key_or_path=EnsureSingleValue("key").of(key, key_option),
        alias=EnsureSingleValue("alias").of(alias, alias_option, allow_none=True),
    ).run()


_alias_remove_argument = typer.Argument(
    None, help=f"The key alias to remove ({REQUIRED_AS_ARG_OR_OPTION}).", show_default=False
)


@key.command(name="remove", param_groups=[WorldOptionsGroup])
async def remove_key(
    ctx: typer.Context,  # noqa: ARG001
    alias: Optional[str] = _alias_remove_argument,
    alias_option: Optional[str] = argument_related_options.alias,
    from_beekeeper: bool = typer.Option(  # noqa: FBT001
        default=False,
        help="Remove the key from the Beekeeper as well.",
    ),
) -> None:
    """Remove a key alias from the profile and optionally from the Beekeeper storage also."""
    from clive.__private.cli.commands.configure.key import RemoveKey

    common = WorldOptionsGroup.get_instance()
    await RemoveKey(
        **common.as_dict(),
        alias=EnsureSingleValue("alias").of(alias, alias_option),
        from_beekeeper=from_beekeeper,
    ).run()
