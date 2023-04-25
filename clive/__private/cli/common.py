from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore
from pydantic import BaseModel

from clive.__private.core.world import World


class Common(BaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    broadcast: bool = typer.Option(False, help="Broadcast the transaction.", show_default=False)
    profile: str = typer.Option(..., help="The profile to use.")
    sign: Optional[str] = typer.Option(None, help="Key alias to sign the transaction with.")
    password: Optional[str] = typer.Option(None, help="The password to use.")
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.")
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
        password: Optional[str] = common.password,  # noqa: ARG001
        save_file: Optional[str] = common.save_file,  # noqa: ARG001
        **kwargs: Any,
    ) -> None:
        with World(profile_name=profile) as world:
            return func(ctx=ctx, **kwargs, world=world)

    return wrapper
