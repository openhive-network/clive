from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any, Optional

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options, update_authority
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.cli.common.update_authority import ApplyCallbackToAuthority, AuthorityType


def get_update_authority_typer(  # noqa: C901, PLR0915
    authority: AuthorityType, apply_callback_to_authority: ApplyCallbackToAuthority
) -> CliveTyper:
    update = CliveTyper(
        name=f"update-{authority}-authority",
        help=f"Add, remove or modify {authority} authority (including weights), set threshold.",
        chain=True,
    )

    help_message = f"Look also at the help for command update-{authority}-authority for more options."

    @pass_context
    def send_update(ctx: Context, /, *args: Any, **kwds: Any) -> None:  # noqa: ARG001
        """Create and send account update operation updating authority asynchronously."""
        from clive.__private.cli.commands.process.account_update import AccountUpdate

        assert isinstance(ctx.obj, AccountUpdate), f"{ctx.command_path} context object is not instance of AccountUpdate"

        async def send_update_async() -> None:
            update_command = ctx.obj
            await update_command.run()

        asyncio_run(send_update_async())

    def assert_context_object(ctx: Context) -> None:
        """Checks that context obj is instance of AccountUpdate."""
        from clive.__private.cli.commands.process.account_update import AccountUpdate

        assert isinstance(ctx.obj, AccountUpdate), f"{ctx.command_path} context object is not instance of AccountUpdate"

    @update.command(name="add-account", help=help_message)
    async def add_account(
        ctx: typer.Context,
        account: str = options.authority_account_name_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Add account authority with weight."""
        assert ctx.parent, f"{ctx.command_path} context parent does not exist"
        assert_context_object(ctx.parent)

        add_account_function = partial(update_authority.add_account, account=account, weight=weight)
        update_function = partial(apply_callback_to_authority, callback=add_account_function)

        update_command = ctx.parent.obj
        update_command.callbacks.append(update_function)

    @update.command(name="add-key", help=help_message)
    async def add_key(
        ctx: typer.Context,
        key: str = options.authority_key_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Add key authority with weight."""
        assert ctx.parent, f"{ctx.command_path} context parent does not exist"
        assert_context_object(ctx.parent)

        add_key_function = partial(update_authority.add_key, key=key, weight=weight)
        update_function = partial(apply_callback_to_authority, callback=add_key_function)

        update_command = ctx.parent.obj
        update_command.callbacks.append(update_function)

    @update.command(name="remove-account", help=help_message)
    async def remove_account(
        ctx: typer.Context,
        account: str = options.authority_account_name_option,
    ) -> None:
        """Remove account authority."""
        assert ctx.parent, f"{ctx.command_path} context parent does not exist"
        assert_context_object(ctx.parent)

        remove_account_function = partial(update_authority.remove_account, account=account)
        update_function = partial(apply_callback_to_authority, callback=remove_account_function)

        update_command = ctx.parent.obj
        update_command.callbacks.append(update_function)

    @update.command(name="remove-key", help=help_message)
    async def remove_key(
        ctx: typer.Context,
        key: str = options.authority_key_option,
    ) -> None:
        """Remove key authority."""
        assert ctx.parent, f"{ctx.command_path} context parent does not exist"
        assert_context_object(ctx.parent)

        remove_key_function = partial(update_authority.remove_key, key=key)
        update_function = partial(apply_callback_to_authority, callback=remove_key_function)

        update_command = ctx.parent.obj
        update_command.callbacks.append(update_function)

    @update.command(name="modify-account", help=help_message)
    async def modify_account(
        ctx: typer.Context,
        account: str = options.authority_account_name_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Modify weight of existing account authority."""
        assert ctx.parent, f"{ctx.command_path} context parent does not exist"
        assert_context_object(ctx.parent)

        modify_account_function = partial(update_authority.modify_account, account=account, weight=weight)
        update_function = partial(apply_callback_to_authority, callback=modify_account_function)

        update_command = ctx.parent.obj
        update_command.callbacks.append(update_function)

    @update.command(name="modify-key", help=help_message)
    async def modify_key(
        ctx: typer.Context,
        key: str = options.authority_key_option,
        weight: int = options.authority_weight_option,
    ) -> None:
        """Modify weight of existing key authority."""
        assert ctx.parent, f"{ctx.command_path} context parent does not exist"
        assert_context_object(ctx.parent)

        modify_key_function = partial(update_authority.modify_key, key=key, weight=weight)
        update_function = partial(apply_callback_to_authority, callback=modify_key_function)

        update_command = ctx.parent.obj
        update_command.callbacks.append(update_function)

    @update.callback(common_options=[OperationCommonOptions], invoke_without_command=True, result_callback=send_update)
    async def set_threshold(
        ctx: typer.Context,
        account_name: str = options.account_name_option,
        threshold: Optional[int] = typer.Option(
            None,
            help="Set Threshold",
            show_default=False,
        ),
        force_offline: bool = typer.Option(
            False,
            help=(
                "By default commands updating authority are performed online. When this flag is enabled transaction"
                " will be prepared offline and list of authorities of selected type will be built from scratch."
            ),
        ),
    ) -> None:
        """Collects common options for add/remove/modify authority, calls chain of commands add/remove/modify at the end of command."""
        from clive.__private.cli.commands.process.account_update import AccountUpdate

        if force_offline:
            typer.confirm(
                (
                    f"Are you sure you want to force prepare transaction offline? Your {authority} authority keys"
                    f" and accounts will be wiped out. Your {authority} authority list will be built from scratch."
                ),
                abort=True,
            )

        operation_common = OperationCommonOptions.get_instance()
        update_command = AccountUpdate(
            **operation_common.as_dict(), account_name=account_name, callbacks=[], offline=force_offline
        )
        if threshold:
            set_threshold_function = partial(update_authority.set_threshold, threshold=threshold)
            update_function = partial(apply_callback_to_authority, callback=set_threshold_function)

            update_command.callbacks.append(update_function)

        ctx.obj = update_command

    return update
