from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parameters import options  # noqa: F811
from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.core._async import asyncio_run
from clive.__private.core.constants.cli import NEW_ACCOUNT_AUTHORITY_THRESOHLD
from schemas.fields.basic import AccountName, PublicKey  # noqa: TC001

if TYPE_CHECKING:
    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation
    from clive.__private.cli.types import AuthorityType


_weight = typer.Option(
    NEW_ACCOUNT_AUTHORITY_THRESOHLD,  # options can't be optional due to how typer works with command chaining
    "--weight",
    help="The new weight of authority",
    show_default=False,
)


account_creation = CliveTyper(name="account-creation", help="Account creation with token or fee.", chain=True)


@pass_context
def send_account_creation(ctx: Context, /, *args: Any, **kwargs: Any) -> None:  # noqa: ARG001
    """
    Create and send account create operation or create claimed account operation.

    Args:
        ctx: The context of the command.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
    """
    typer.echo("sending transaction here")

    async def send_account_creation_async() -> None:
        account_update_command = ctx.obj
        await account_update_command.run()

    # make specify-keys mutually exclusive with specify-xxx-authority
    asyncio_run(send_account_creation_async())


def _get_command_from_context(ctx: typer.Context) -> ProcessAccountCreation:
    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation  # noqa: PLC0415

    assert ctx.parent, f"{ctx.command_path} context parent does not exist"
    account_creation_command = ctx.parent.obj
    assert isinstance(account_creation_command, ProcessAccountCreation), (
        f"{ctx.parent.command_path} context object is not instance of ProcessAccountCreation"
    )
    return account_creation_command


def add_key_authority_to_command(ctx: typer.Context, type_: AuthorityType, key: PublicKey, weight: int) -> None:
    """
    Add new key authority to command ProcessAccountCreation stored in context.

    Args:
        ctx: The context of the command.
        type_: Type of authority to modify (owner, active or posting).
        key: The public key to add.
        weight: The weight of key authority.
    """
    _get_command_from_context(ctx).add_key_authority(type_, key, weight)


def add_account_authority_to_command(
    ctx: typer.Context, type_: AuthorityType, account: AccountName, weight: int
) -> None:
    """
    Add new account authority to command ProcessAccountCreation stored in context.

    Args:
        ctx: The context of the command.
        type_: Type of authority to modify (owner, active or posting).
        account: The account authority to add.
        weight: The weight of account authority.
    """
    _get_command_from_context(ctx).add_account_authority(type_, account, weight)


@account_creation.callback(result_callback=send_account_creation)
async def process_account_creation(  # noqa: PLR0913
    ctx: typer.Context,
    creator: str = modified_param(options.working_account_template, param_decls=("--creator",)),
    new_account_name: str = typer.Option(
        ...,
        help="The name of the new account.",
    ),
    fee: bool = typer.Option(  # noqa: FBT001
        default=False,
        help="If set to true then account creation fee will be paid, you can check it with command `clive show chain`."
        " If set to false then new account token will be used.",
    ),
    json_metadata: str = typer.Option(
        "",
        help="The json metadata of the new account.",
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Create new account."""
    from clive.__private.cli.commands.process.process_account_creation import (  # noqa: PLC0415
        ProcessAccountCreation,
    )

    account_creation_command = ProcessAccountCreation(
        creator=creator,
        new_account_name=new_account_name,
        fee=fee,
        json_metadata=json_metadata,
        sign=sign,
        broadcast=broadcast,
        save_file=save_file,
    )
    ctx.obj = account_creation_command


@account_creation.command(name="specify-keys", help="Simple authority.")
async def specify_keys(  # noqa: PLR0913
    ctx: typer.Context,
    owner_key: str = typer.Option(
        ...,
        "--owner",
        help="The public key of owner key authority.",
        show_default=False,
    ),
    active_key: str = typer.Option(
        ...,
        "--active",
        help="The public key of active key authority.",
        show_default=False,
    ),
    posting_key: str = typer.Option(
        ...,
        "--posting",
        help="The public key of posting key authority.",
        show_default=False,
    ),
    memo_key: str = typer.Option(
        ...,
        "--memo",
        help="The public key of memo key.",
        show_default=False,
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Add public key to authority."""
    command = _get_command_from_context(ctx)
    command.add_key_authority("owner", owner_key, NEW_ACCOUNT_AUTHORITY_THRESOHLD)
    command.add_key_authority("active", active_key, NEW_ACCOUNT_AUTHORITY_THRESOHLD)
    command.add_key_authority("posting", posting_key, NEW_ACCOUNT_AUTHORITY_THRESOHLD)
    command.set_memo_key(memo_key)
    command.sign = sign
    command.broadcast = broadcast
    command.save_file = save_file
    typer.echo(f"from specify_keys callback")


specify_owner_authority = CliveTyper(
    name="specify-owner-authority", help="Possibly complex owner authority.", chain=True
)


@specify_owner_authority.callback(invoke_without_command=True)
async def owner_set_threshold(
    ctx: typer.Context,
    threshold: int = typer.Option(
        1,
        help="Set threshold for owner authority.",
        show_default=True,
    ),
) -> None:
    """Collect common options for add/remove/modify authority, calls chain of commands at the end of command."""
    _get_command_from_context(ctx).set_threshold("owner", threshold)


@specify_owner_authority.command(name="add-key")
async def owner_add_key(
    ctx: typer.Context,
    key: str = typer.Option(
        ...,
        "--key",
        help="The public key to add",
        show_default=False,
    ),
    weight: int = _weight,
) -> None:
    """Add public key to authority."""
    _get_command_from_context(ctx).add_key_authority("owner", key, weight)
    typer.echo("from specify_owner_authority add_key")


@specify_owner_authority.command(name="add-account")
async def owner_add_account(
    ctx: typer.Context,
    account_name: str = typer.Option(
        ...,
        "--account-name",
        help="The public account to add",
        show_default=False,
    ),
    weight: int = _weight,
) -> None:
    """Add public account to authority."""
    _get_command_from_context(ctx).add_account_authority("owner", account_name, weight)
    typer.echo("from specify_owner_authority add_account")


account_creation.add_typer(specify_owner_authority)


specify_active_authority = CliveTyper(
    name="specify-active-authority", help="Possibly complex active authority.", chain=True
)


@specify_active_authority.callback(invoke_without_command=True)
async def active_set_threshold(
    ctx: typer.Context,
    threshold: int = typer.Option(
        1,
        help="Set threshold for owner authority.",
        show_default=True,
    ),
) -> None:
    """Collect common options for add/remove/modify authority, calls chain of commands at the end of command."""
    _get_command_from_context(ctx).set_threshold("active", threshold)


@specify_active_authority.command(name="add-key")
async def active_add_key(
    ctx: typer.Context,
    key: str = typer.Option(
        ...,
        "--key",
        help="The public key to add",
        show_default=False,
    ),
    weight: int = _weight,
) -> None:
    """Add public key to authority."""
    _get_command_from_context(ctx).add_key_authority("active", key, weight)
    typer.echo("from specify_active_authority add_key")


@specify_active_authority.command(name="add-account")
async def active_add_account(
    ctx: typer.Context,
    account_name: str = typer.Option(
        ...,
        "--account-name",
        help="The public account to add",
        show_default=False,
    ),
    weight: int = _weight,
) -> None:
    """Add public account to authority."""
    _get_command_from_context(ctx).add_account_authority("active", account_name, weight)
    typer.echo("from specify_active_authority add_account")


specify_owner_authority.add_typer(specify_active_authority)


specify_posting_authority = CliveTyper(
    name="specify-posting-authority", help="Possibly complex posting authority.", chain=True
)


@specify_posting_authority.callback(invoke_without_command=True)
async def posting_set_threshold(
    ctx: typer.Context,
    threshold: int = typer.Option(
        1,
        help="Set threshold for owner authority.",
        show_default=True,
    ),
) -> None:
    """Collect common options for add/remove/modify authority, calls chain of commands at the end of command."""
    _get_command_from_context(ctx).set_threshold("posting", threshold)


@specify_posting_authority.command(name="add-key")
async def posting_add_key(
    ctx: typer.Context,
    key: str = typer.Option(
        ...,
        "--key",
        help="The public key to add",
        show_default=False,
    ),
    weight: int = _weight,
) -> None:
    """Add public key to authority."""
    _get_command_from_context(ctx).add_key_authority("posting", key, weight)
    typer.echo("from specify_posting_authority add_key")


@specify_posting_authority.command(name="add-account")
async def posting_add_account(
    ctx: typer.Context,
    account_name: str = typer.Option(
        ...,
        "--account-name",
        help="The public account to add",
        show_default=False,
    ),
    weight: int = _weight,
) -> None:
    """Add public account to authority."""
    _get_command_from_context(ctx).add_account_authority("posting", account_name, weight)
    typer.echo("from specify_posting_authority add_account")


@specify_posting_authority.command(name="specify-memo-key")
async def memo_key(
    ctx: typer.Context,
    key: str = typer.Option(
        "for demonstration purposes",
        "--key",
        help="The public account to add",
        show_default=False,
    ),
    sign: str | None = options.sign,
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Add public account to authority."""
    command = _get_command_from_context(ctx)
    command.set_memo_key(key)
    command.sign = sign
    command.broadcast = broadcast
    command.save_file = save_file
    typer.echo("from specify_memo_key")


specify_active_authority.add_typer(specify_posting_authority)
