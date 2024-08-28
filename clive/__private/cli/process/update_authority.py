from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, Optional

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.cli.types import AccountUpdateFunction
    from clive.__private.core.types import AuthorityType


@pass_context
def send_update(ctx: Context, /, *args: Any, **kwds: Any) -> None:  # noqa: ARG001
    """Create and send account update operation updating authority asynchronously."""
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate

    assert isinstance(
        ctx.obj, ProcessAccountUpdate
    ), f"{ctx.command_path} context object is not instance of ProcessAccountUpdate"

    async def send_update_async() -> None:
        update_command = ctx.obj
        await update_command.run()

    asyncio_run(send_update_async())


def add_callback_to_update_command(ctx: typer.Context, callback: AccountUpdateFunction) -> None:
    """Add callback modifying authority to command ProcessAccountUpdate stored in context."""
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate

    assert ctx.parent, f"{ctx.command_path} context parent does not exist"
    update_command = ctx.parent.obj
    assert isinstance(
        update_command, ProcessAccountUpdate
    ), f"{ctx.parent.command_path} context object is not instance of ProcessAccountUpdate"
    update_command.add_callback(callback)


def get_update_authority_typer(authority: AuthorityType) -> CliveTyper:
    epilog = f"Look also at the help for command update-{authority}-authority for more options."
    update = CliveTyper(
        name=f"update-{authority}-authority",
        help=f"Add, remove or modify {authority} authority (including weights), set threshold.",
        chain=True,
    )

    @update.command(name="add-account", epilog=epilog)
    async def add_account(
        ctx: typer.Context,
        account: str = options.authority_account_name_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Add account authority with weight."""
        from clive.__private.cli.commands.process.process_account_update import add_account, update_authority

        add_account_function = partial(add_account, account=account, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=add_account_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="add-key", epilog=epilog)
    async def add_key(
        ctx: typer.Context,
        key: str = options.authority_key_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Add key authority with weight."""
        from clive.__private.cli.commands.process.process_account_update import add_key, update_authority

        add_key_function = partial(add_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=add_key_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="remove-account", epilog=epilog)
    async def remove_account(
        ctx: typer.Context,
        account: str = options.authority_account_name_option,
    ) -> None:
        """Remove account authority."""
        from clive.__private.cli.commands.process.process_account_update import remove_account, update_authority

        remove_account_function = partial(remove_account, account=account)
        update_function = partial(update_authority, attribute=authority, callback=remove_account_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="remove-key", epilog=epilog)
    async def remove_key(
        ctx: typer.Context,
        key: str = options.authority_key_option,
    ) -> None:
        """Remove key authority."""
        from clive.__private.cli.commands.process.process_account_update import remove_key, update_authority

        remove_key_function = partial(remove_key, key=key)
        update_function = partial(update_authority, attribute=authority, callback=remove_key_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="modify-account", epilog=epilog)
    async def modify_account(
        ctx: typer.Context,
        account: str = options.authority_account_name_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Modify weight of existing account authority."""
        from clive.__private.cli.commands.process.process_account_update import modify_account, update_authority

        modify_account_function = partial(modify_account, account=account, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=modify_account_function)
        add_callback_to_update_command(ctx, update_function)

    @update.command(name="modify-key", epilog=epilog)
    async def modify_key(
        ctx: typer.Context,
        key: str = options.authority_key_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Modify weight of existing key authority."""
        from clive.__private.cli.commands.process.process_account_update import modify_key, update_authority

        modify_key_function = partial(modify_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=authority, callback=modify_key_function)
        add_callback_to_update_command(ctx, update_function)

    @update.callback(common_options=[OperationCommonOptions], invoke_without_command=True, result_callback=send_update)
    async def set_threshold(
        ctx: typer.Context,
        account_name: str = options.account_name_option,
        threshold: Optional[int] = typer.Option(
            None,
            help="Set Threshold",
            show_default=False,
        ),
    ) -> None:
        """Collect common options for add/remove/modify authority, calls chain of commands at the end of command."""
        from clive.__private.cli.commands.process.process_account_update import (
            ProcessAccountUpdate,
            set_threshold,
            update_authority,
        )

        operation_common = OperationCommonOptions.get_instance()
        update_command = ProcessAccountUpdate(**operation_common.as_dict(), account_name=account_name)
        if threshold:
            set_threshold_function = partial(set_threshold, threshold=threshold)
            update_function = partial(update_authority, attribute=authority, callback=set_threshold_function)

            update_command.add_callback(update_function)

        ctx.obj = update_command

    return update
