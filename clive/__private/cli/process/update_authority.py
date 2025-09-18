from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parameters import modified_param
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue
from clive.__private.core._async import asyncio_run
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION
from clive.__private.cli.common.parameters.argument_related_options import _make_argument_related_option

if TYPE_CHECKING:
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate
    from clive.__private.cli.types import AccountUpdateFunction, AuthorityType


_authority_account_name = typer.Option(
    ...,
    "--account",
    help="The account to  add/remove/modify (account must exist).",
)
_authority_key = typer.Option(
    ...,
    "--key",
    help="The public key to add/remove/modify",
)
_authority_weight = typer.Option(
    1,
    "--weight",
    help="The new weight of account/key authority",
)
_optional_broadcast = modified_param(options.broadcast, default=None)


@pass_context
def send_update(ctx: Context, /, *args: Any, **kwargs: Any) -> None:  # noqa: ARG001
    """
    Create and send account update operation updating authority asynchronously.

    Args:
        ctx: The context of the command.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
    """
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate  # noqa: PLC0415

    assert isinstance(ctx.obj, ProcessAccountUpdate), (
        f"{ctx.command_path} context object is not instance of ProcessAccountUpdate"
    )

    async def send_update_async() -> None:
        update_command = ctx.obj
        await update_command.run()

    asyncio_run(send_update_async())


def _get_update_command_from_context_parent(ctx: typer.Context) -> ProcessAccountUpdate:
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate  # noqa: PLC0415

    assert ctx.parent, f"{ctx.command_path} context parent does not exist"
    update_command = ctx.parent.obj
    assert isinstance(update_command, ProcessAccountUpdate), (
        f"{ctx.parent.command_path} context object is not instance of ProcessAccountUpdate"
    )
    return update_command


def add_callback_to_update_command(ctx: typer.Context, callback: AccountUpdateFunction) -> None:
    """
    Add callback modifying authority to command ProcessAccountUpdate stored in context.

    Args:
        ctx: The context of the command.
        callback: The callback function to add to the update command.
    """
    _get_update_command_from_context_parent(ctx).add_callback(callback)


def modify_command_common_options(
    ctx: typer.Context,
    sign_with: str | None,
    broadcast: bool | None,  # noqa: FBT001
    save_file: str | None,
) -> None:
    _get_update_command_from_context_parent(ctx).modify_common_options(
        sign_with=sign_with, broadcast=broadcast, save_file=save_file
    )


def get_update_authority_typer(authority: AuthorityType) -> CliveTyper:  # noqa: PLR0915
    epilog = f"Look also at the help for command update-{authority}-authority for more options."
    update = CliveTyper(
        name=f"update-{authority}-authority",
        help=f"Add, remove or modify {authority} authority (including weights), set threshold.",
        chain=True,
    )

    @update.command(name="add-account", epilog=epilog)
    async def add_account(  # noqa: PLR0913
        ctx: typer.Context,
        account: str = typer.Argument(
            None,
            help=f"The account to  add/remove/modify (account must exist, {REQUIRED_AS_ARG_OR_OPTION}).",
        ),
        account_option: str = _make_argument_related_option("--account"),
        weight: int = _authority_weight,
        sign_with: str | None = options.sign_with,
        broadcast: bool | None = _optional_broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """Add account authority with weight."""
        from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
            add_account,
            update_authority,
        )

        add_account_function = partial(add_account, account=EnsureSingleValue("account").of(account, account_option), weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=add_account_function)
        add_callback_to_update_command(ctx, update_function)
        modify_command_common_options(ctx, sign_with, broadcast, save_file)

    @update.command(name="add-key", epilog=epilog)
    async def add_key(  # noqa: PLR0913
        ctx: typer.Context,
        key: str = _authority_key,
        weight: int = _authority_weight,
        sign_with: str | None = options.sign_with,
        broadcast: bool | None = _optional_broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """Add key authority with weight."""
        from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
            add_key,
            update_authority,
        )

        add_key_function = partial(add_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=add_key_function)
        add_callback_to_update_command(ctx, update_function)
        modify_command_common_options(ctx, sign_with, broadcast, save_file)

    @update.command(name="remove-account", epilog=epilog)
    async def remove_account(
        ctx: typer.Context,
        account: str = _authority_account_name,
        sign_with: str | None = options.sign_with,
        broadcast: bool | None = _optional_broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """Remove account authority."""
        from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
            remove_account,
            update_authority,
        )

        remove_account_function = partial(remove_account, account=account)
        update_function = partial(update_authority, attribute=authority, callback=remove_account_function)
        add_callback_to_update_command(ctx, update_function)
        modify_command_common_options(ctx, sign_with, broadcast, save_file)

    @update.command(name="remove-key", epilog=epilog)
    async def remove_key(
        ctx: typer.Context,
        key: str = _authority_key,
        sign_with: str | None = options.sign_with,
        broadcast: bool | None = _optional_broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """Remove key authority."""
        from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
            remove_key,
            update_authority,
        )

        remove_key_function = partial(remove_key, key=key)
        update_function = partial(update_authority, attribute=authority, callback=remove_key_function)
        add_callback_to_update_command(ctx, update_function)
        modify_command_common_options(ctx, sign_with, broadcast, save_file)

    @update.command(name="modify-account", epilog=epilog)
    async def modify_account(  # noqa: PLR0913
        ctx: typer.Context,
        account: str = _authority_account_name,
        weight: int = _authority_weight,
        sign_with: str | None = options.sign_with,
        broadcast: bool | None = _optional_broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """Modify weight of existing account authority."""
        from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
            modify_account,
            update_authority,
        )

        modify_account_function = partial(modify_account, account=account, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=modify_account_function)
        add_callback_to_update_command(ctx, update_function)
        modify_command_common_options(ctx, sign_with, broadcast, save_file)

    @update.command(name="modify-key", epilog=epilog)
    async def modify_key(  # noqa: PLR0913
        ctx: typer.Context,
        key: str = _authority_key,
        weight: int = _authority_weight,
        sign_with: str | None = options.sign_with,
        broadcast: bool | None = _optional_broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """Modify weight of existing key authority."""
        from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
            modify_key,
            update_authority,
        )

        modify_key_function = partial(modify_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=modify_key_function)
        add_callback_to_update_command(ctx, update_function)
        modify_command_common_options(ctx, sign_with, broadcast, save_file)

    @update.callback(invoke_without_command=True, result_callback=send_update)
    async def set_threshold(  # noqa: PLR0913
        ctx: typer.Context,
        account_name: str = options.account_name,
        threshold: int | None = typer.Option(
            None,
            help="Set Threshold",
        ),
        sign_with: str | None = options.sign_with,
        broadcast: bool = options.broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """Collect common options for add/remove/modify authority, calls chain of commands at the end of command."""
        from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
            ProcessAccountUpdate,
            set_threshold,
            update_authority,
        )

        update_command = ProcessAccountUpdate(
            account_name=account_name,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
        )
        if threshold:
            set_threshold_function = partial(set_threshold, threshold=threshold)
            update_function = partial(update_authority, attribute=authority, callback=set_threshold_function)

            update_command.add_callback(update_function)

        ctx.obj = update_command

    return update
