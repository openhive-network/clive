from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.cli.types import AccountUpdateFunction, AuthorityType


_authority_account_name = typer.Option(
    ...,
    "--account",
    help="The account to  add/remove/modify (account must exist).",
    show_default=False,
)
_authority_key = typer.Option(
    ...,
    "--key",
    help="The public key to add/remove/modify",
    show_default=False,
)
_authority_weight = typer.Option(
    ...,
    "--weight",
    help="The new weight of account/key authority",
    show_default=False,
)


@pass_context
def send_update(ctx: Context, /, *args: Any, **kwds: Any) -> None:  # noqa: ARG001
    """
    Create and send account update operation updating authority asynchronously.

    Args:
        ctx: The context of the command.
        *args: Additional positional arguments (not used).
        **kwds: Additional keyword arguments (not used).

    Raises:
        AssertionError: If the context object is not an instance of ProcessAccountUpdate.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate

    assert isinstance(ctx.obj, ProcessAccountUpdate), (
        f"{ctx.command_path} context object is not instance of ProcessAccountUpdate"
    )

    async def send_update_async() -> None:
        update_command = ctx.obj
        await update_command.run()

    asyncio_run(send_update_async())


def add_callback_to_update_command(ctx: typer.Context, callback: AccountUpdateFunction) -> None:
    """
    Add callback modifying authority to command ProcessAccountUpdate stored in context.

    Args:
        ctx: The context of the command.
        callback: The callback function to add to the update command.

    Raises:
        AssertionError: If the context parent does not exist or is not an instance of ProcessAccountUpdate.

    Returns:
        None
    """
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate

    assert ctx.parent, f"{ctx.command_path} context parent does not exist"
    update_command = ctx.parent.obj
    assert isinstance(update_command, ProcessAccountUpdate), (
        f"{ctx.parent.command_path} context object is not instance of ProcessAccountUpdate"
    )
    update_command.add_callback(callback)


def get_update_authority_typer(authority: AuthorityType) -> CliveTyper:
    """
    Get update authority command typer for a specific authority type.

    Args:
        authority: The type of authority to update (e.g., "owner", "active", "posting").

    Returns:
        CliveTyper: A CliveTyper instance for the update authority command.
    """
    epilog = f"Look also at the help for command update-{authority}-authority for more options."
    update = CliveTyper(
        name=f"update-{authority}-authority",
        help=f"Add, remove or modify {authority} authority (including weights), set threshold.",
        chain=True,
    )

    @update.command(name="add-account", epilog=epilog)
    async def add_account(
        ctx: typer.Context,
        account: str = _authority_account_name,
        weight: int = _authority_weight,
    ) -> None:
        """
        Add account authority with weight.

        Args:
            ctx: The context of the command.
            account: The account name to add as authority.
            weight: The weight of the authority to be added.

        Returns:
            None
        """
        from clive.__private.cli.commands.process.process_account_update import add_account, update_authority

        add_account_function = partial(add_account, account=account, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=add_account_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="add-key", epilog=epilog)
    async def add_key(
        ctx: typer.Context,
        key: str = _authority_key,
        weight: int = _authority_weight,
    ) -> None:
        """
        Add key authority with weight.

        Args:
            ctx: The context of the command.
            key: The public key to add as authority.
            weight: The weight of the authority to be added.

        Returns:
            None
        """
        from clive.__private.cli.commands.process.process_account_update import add_key, update_authority

        add_key_function = partial(add_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=add_key_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="remove-account", epilog=epilog)
    async def remove_account(
        ctx: typer.Context,
        account: str = _authority_account_name,
    ) -> None:
        """
        Remove account authority.

        Args:
            ctx: The context of the command.
            account: The account name to remove from authority.

        Returns:
            None
        """
        from clive.__private.cli.commands.process.process_account_update import remove_account, update_authority

        remove_account_function = partial(remove_account, account=account)
        update_function = partial(update_authority, attribute=authority, callback=remove_account_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="remove-key", epilog=epilog)
    async def remove_key(
        ctx: typer.Context,
        key: str = _authority_key,
    ) -> None:
        """
        Remove key authority.

        Args:
            ctx: The context of the command.
            key: The public key to remove from authority.

        Returns:
            None
        """
        from clive.__private.cli.commands.process.process_account_update import remove_key, update_authority

        remove_key_function = partial(remove_key, key=key)
        update_function = partial(update_authority, attribute=authority, callback=remove_key_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="modify-account", epilog=epilog)
    async def modify_account(
        ctx: typer.Context,
        account: str = _authority_account_name,
        weight: int = _authority_weight,
    ) -> None:
        """
        Modify weight of existing account authority.

        Args:
            ctx: The context of the command.
            account: The account name to modify authority weight.
            weight: The new weight of the authority.

        Returns:
            None
        """
        from clive.__private.cli.commands.process.process_account_update import modify_account, update_authority

        modify_account_function = partial(modify_account, account=account, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=modify_account_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="modify-key", epilog=epilog)
    async def modify_key(
        ctx: typer.Context,
        key: str = _authority_key,
        weight: int = _authority_weight,
    ) -> None:
        """
        Modify weight of existing key authority.

        Args:
            ctx: The context of the command.
            key: The public key to modify authority weight.
            weight: The new weight of the authority.

        Returns:
            None
        """
        from clive.__private.cli.commands.process.process_account_update import modify_key, update_authority

        modify_key_function = partial(modify_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=modify_key_function)
        add_callback_to_update_command(ctx, update_function)

    @update.callback(invoke_without_command=True, result_callback=send_update)
    async def set_threshold(  # noqa: PLR0913
        ctx: typer.Context,
        account_name: str = options.account_name,
        threshold: int | None = typer.Option(
            None,
            help="Set Threshold",
            show_default=False,
        ),
        sign: str | None = options.sign,
        broadcast: bool = options.broadcast,  # noqa: FBT001
        save_file: str | None = options.save_file,
    ) -> None:
        """
        Collect common options for add/remove/modify authority, calls chain of commands at the end of command.

        Args:
            ctx: The context of the command.
            account_name: The name of the account to update.
            threshold: The new threshold to set for the authority.
            sign: The signature option for the command.
            broadcast: Whether to broadcast the transaction.
            save_file: The file to save the transaction to.

        Returns:
            None
        """
        from clive.__private.cli.commands.process.process_account_update import (
            ProcessAccountUpdate,
            set_threshold,
            update_authority,
        )

        update_command = ProcessAccountUpdate(
            account_name=account_name,
            sign=sign,
            broadcast=broadcast,
            save_file=save_file,
        )
        if threshold:
            set_threshold_function = partial(set_threshold, threshold=threshold)
            update_function = partial(update_authority, attribute=authority, callback=set_threshold_function)

            update_command.add_callback(update_function)

        ctx.obj = update_command

    return update
