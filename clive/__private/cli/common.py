from collections.abc import Callable
from functools import wraps
from os import environ
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore
from pydantic import BaseModel
from typing_extensions import Self

from clive.__private.core.world import World
from clive.__private.ui.app import Clive


class DummyOpen:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: Any, **__: Any) -> None:
        """TODO document why this method is empty"""


def get_world(profile: str) -> World | DummyOpen:
    if "_CLIVE_COMPLETE" in environ:
        return DummyOpen()

    if not Clive.is_app_exist():
        return World(profile_name=profile)
    return Clive.app_instance().world


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
        with get_world(profile) as world:
            return func(ctx=ctx, **kwargs, world=world)

    return wrapper
