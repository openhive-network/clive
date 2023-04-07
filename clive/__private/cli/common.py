from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore
from pydantic import BaseModel


class Common(BaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    broadcast: bool = typer.Option(..., help="Broadcast the transaction.", show_default=False)
    sign: Optional[str] = typer.Option(..., help="Key alias to sign the transaction with.")
    profile: Optional[str] = typer.Option(..., help="The profile to use.")
    password: Optional[str] = typer.Option(..., help="The password to use.")
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.")


def common_options(func: Callable[..., None]) -> Any:
    @merge_args(func)
    @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
    def wrapper(
        ctx: typer.Context,
        broadcast: bool = Common().broadcast,  # noqa: ARG001
        sign: Optional[str] = Common().sign,  # noqa: ARG001
        profile: Optional[str] = Common().profile,  # noqa: ARG001
        password: Optional[str] = Common().password,  # noqa: ARG001
        save_file: Optional[str] = Common().save_file,  # noqa: ARG001
        **kwargs: Any,
    ) -> None:
        return func(ctx=ctx, **kwargs)

    return wrapper
