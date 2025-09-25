from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from click import Context

    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate


def get_command_from_context[T](ctx: Context, command_type: type[T]) -> T:
    """
    Recursively searches the current or parent Context for an object of the given command_type.

    Args:
        ctx: context of cli (click/typer) command where should be stored command object (instance of type T).
        command_type: type (command class) of command object to search for.

    Returns:
        The parsed frequency.
    """
    if not isinstance(ctx.obj, command_type):
        assert ctx.parent, (
            f"{ctx.command_path} "
            f"context or context parent should contain {command_type.__name__} "
            "but context parent does not exist"
        )
        return get_command_from_context(ctx.parent, command_type)
    return ctx.obj


def get_process_account_creation_command(ctx: Context) -> ProcessAccountCreation:
    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation  # noqa: PLC0415

    return get_command_from_context(ctx, ProcessAccountCreation)


def get_process_account_update_command(ctx: Context) -> ProcessAccountUpdate:
    from clive.__private.cli.commands.process.process_account_update import ProcessAccountUpdate  # noqa: PLC0415

    return get_command_from_context(ctx, ProcessAccountUpdate)
