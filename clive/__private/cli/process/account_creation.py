from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parsers import hive_asset
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.models import Asset

account_creation = CliveTyper(name="account-creation", help="Account creation with token or fee.", chain=True)


@pass_context
def send_account_create(ctx: Context, /, *args: Any, **kwargs: Any) -> None:  # noqa: ARG001
    """
    Create and send account create operation (takes fee) or create claimed account operation (takes account creation token).

    Args:
        ctx: The context of the command.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
    """
    typer.echo("sending transaction here")

    async def send_account_create_async() -> None:
        account_update_command = ctx.obj
        await account_update_command.run()

    # make specify-keys mutually exclusive with specify-xxx-authority
    # asyncio_run(send_account_create_async())  # noqa


@account_creation.callback(result_callback=send_account_create)
async def process_account_creation(
    ctx: typer.Context,
    new_account_name: str = typer.Option(
        ...,
        help="The name of the new account.",
    ),
    fee: bool = typer.Option(
        False,
        help="If set to true then account creation fee will be paid, you can check it with command `clive show chain`."
         " If set to false then new account token will be used.",
    ),
) -> None:
    """Create new account."""
    from clive.__private.cli.commands.process.process_account_creation import (  # noqa: PLC0415
        AccountCreation,
    )

    account_creation_command = AccountCreation(
        new_account_name=new_account_name,
        fee=fee,
    )
    ctx.obj = account_creation_command



@account_creation.command(name="specify-keys", help="Simple authority.")
async def new_keys(
    owner_key: str = typer.Option(
        ...,
        "--owner",
        help="The public key to add",
        show_default=False,
    ),
    active_key: str = typer.Option(
        ...,
        "--active",
        help="The public key to add",
        show_default=False,
    ),
    posting_key: str = typer.Option(
        ...,
        "--posting",
        help="The public key to add",
        show_default=False,
    ),
    memo_key: str = typer.Option(
        ...,
        "--memo",
        help="The public key to add",
        show_default=False,
    ),
) -> None:
    """Add public key to authority."""

    typer.echo(f"from specify_keys callback, locals: {locals()}")



specify_owner_authority = CliveTyper(name="specify-owner-authority", help="Possibly complex owner authority.", chain=True)

@specify_owner_authority.command(name="add-key")
async def add_key(
    key: str = typer.Option(
        ...,
        "--key",
        help="The public key to add",
        show_default=False,
    ),
    weight: int = typer.Option(
        1,
        "--weight",
        help="The new weight of key authority",
        show_default=False,
    ),
) -> None:
    """Add public key to authority."""

    typer.echo(f"from specify_owner_authority add_key")

@specify_owner_authority.command(name="add-account")
async def add_account(
    account_name: str = typer.Option(
        ...,
        "--account-name",
        help="The public account to add",
        show_default=False,
    ),
    weight: int = typer.Option(
        1,
        "--weight",
        help="The new weight of account authority",
        show_default=False,
    ),
) -> None:
    """Add public account to authority."""

    typer.echo(f"from specify_owner_authority add_account")

account_creation.add_typer(specify_owner_authority)


specify_active_authority = CliveTyper(name="specify-active-authority", help="Possibly complex active authority.", chain=True)

@specify_active_authority.command(name="add-key")
async def add_key(
    key: str = typer.Option(
        ...,
        "--key",
        help="The public key to add",
        show_default=False,
    ),
    weight: int = typer.Option(
        1,
        "--weight",
        help="The new weight of key authority",
        show_default=False,
    ),
) -> None:
    """Add public key to authority."""

    typer.echo(f"from specify_active_authority add_key")

@specify_active_authority.command(name="add-account")
async def add_account(
    account_name: str = typer.Option(
        ...,
        "--account-name",
        help="The public account to add",
        show_default=False,
    ),
    weight: int = typer.Option(
        1,
        "--weight",
        help="The new weight of account authority",
        show_default=False,
    ),
) -> None:
    """Add public account to authority."""
    typer.echo(f"from specify_active_authority add_account")

specify_owner_authority.add_typer(specify_active_authority)


specify_posting_authority = CliveTyper(name="specify-posting-authority", help="Possibly complex posting authority.", chain=True)

@specify_posting_authority.command(name="add-key")
async def add_key(
    key: str = typer.Option(
        ...,
        "--key",
        help="The public key to add",
        show_default=False,
    ),
    weight: int = typer.Option(
        1,
        "--weight",
        help="The new weight of key authority",
        show_default=False,
    ),
) -> None:
    """Add public key to authority."""

    typer.echo(f"from specify_posting_authority add_key")

@specify_posting_authority.command(name="add-account")
async def add_account(
    account_name: str = typer.Option(
        ...,
        "--account-name",
        help="The public account to add",
        show_default=False,
    ),
    weight: int = typer.Option(
        1,
        "--weight",
        help="The new weight of account authority",
        show_default=False,
    ),
) -> None:
    """Add public account to authority."""
    typer.echo(f"from specify_posting_authority add_account")

@specify_posting_authority.command(name="specify-memo-key")
async def memo_key(
    key: str = typer.Option(
        "for demonstration purposes",
        "--key",
        help="The public account to add",
        show_default=False,
    ),
) -> None:
    """Add public account to authority."""
    typer.echo(f"from specify_memo_key")

specify_active_authority.add_typer(specify_posting_authority)


