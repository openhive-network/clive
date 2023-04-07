from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore
from pydantic import BaseModel

from clive.__private.core.world import World
from clive.__private.util import ExitCallHandler


class Common(BaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    broadcast: bool = typer.Option(..., help="Broadcast the transaction.", show_default=False)
    profile: str = typer.Option(..., help="The profile to use.", show_default=False)
    sign: Optional[str] = typer.Option(None, help="Key alias to sign the transaction with.", show_default=False)
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.", show_default=False)
    world: World | None = None

    class Config:
        arbitrary_types_allowed: bool = True


def common_options(func: Callable[..., None]) -> Any:
    common = Common()

    @merge_args(func)
    @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
    def wrapper(
        ctx: typer.Context,
        broadcast: bool = common.broadcast,  # noqa: ARG001
        sign: Optional[str] = common.sign,  # noqa: ARG001
        profile: str = common.profile,
        save_file: Optional[str] = common.save_file,  # noqa: ARG001
        **kwargs: Any,
    ) -> None:
        with ExitCallHandler(World(profile_name=profile), finally_callback=lambda w: w.close()) as world:
            ctx.params.update(world=world)
            return func(ctx=ctx, **kwargs)

    return wrapper


def get_args_from_typer_function(function: Callable[..., None]) -> list[tuple[str, str]]:
    """Get the arguments from a typer function.

    Args:
        function: The typer function to get the arguments from.

    Returns:
        A list of tuples containing the argument name and help text.
    """
    collected = []
    for k, v in signature(function).parameters.items():
        option_info = v.default
        collected.append((k, option_info.help))

    return collected
