from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, Concatenate, Optional, ParamSpec

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import PreconfiguredBaseModel

if TYPE_CHECKING:
    from clive.__private.core.world import World


P = ParamSpec("P")

PreWrapFuncT = Callable[Concatenate[typer.Context, P], None]
PostWrapFuncT = Callable[Concatenate[typer.Context, P], None]


class OperationCommon(PreconfiguredBaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    profile: str = options.profile_option
    password: str = typer.Option(..., help="Password to unlock the wallet.", show_default=False)
    sign: str = typer.Option(..., help="Key alias to sign the transaction with.", show_default=False)
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option
    broadcast: bool = typer.Option(..., help="Whether broadcast the transaction. (i.e. dry-run)", show_default=False)
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.", show_default=False)
    world: "World"

    @classmethod
    def decorator(cls, func: PreWrapFuncT[P]) -> PostWrapFuncT[P]:
        common = cls.construct(world=None)  # type: ignore[arg-type]

        @merge_args(func)
        @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
        def wrapper(
            ctx: typer.Context,
            profile: str = common.profile,
            password: str = common.password,
            sign: str = common.sign,  # noqa: ARG001
            beekeeper_remote: Optional[str] = common.beekeeper_remote,
            broadcast: bool = common.broadcast,
            save_file: Optional[str] = common.save_file,  # noqa: ARG001
            *args: P.args,
            **kwargs: Any,
        ) -> None:
            from clive.__private.core.exit_call_handler import ExitCallHandler
            from clive.__private.core.world import TyperWorld
            from clive.core.url import Url

            if not broadcast:
                typer.echo("[Performing dry run, because --no-broadcast was specified.]\n")

            beekeeper_remote_endpoint = Url.parse(beekeeper_remote) if beekeeper_remote else None

            cls._print_launching_beekeeper(beekeeper_remote_endpoint)

            with ExitCallHandler(
                TyperWorld(
                    profile_name=profile,
                    beekeeper_remote_endpoint=beekeeper_remote_endpoint,
                ),
                finally_callback=lambda w: w.close(),
            ) as world:
                cls._assert_correct_profile_is_loaded(world.profile_data.name, profile)

                ctx.params.update(world=world)

                world.beekeeper.api.unlock(wallet_name=world.profile_data.name, password=password)

                func(ctx, *args, **kwargs)

        return wrapper  # type: ignore[no-any-return]

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.world import World  # noqa: F401

        OperationCommon.update_forward_refs(**locals())
