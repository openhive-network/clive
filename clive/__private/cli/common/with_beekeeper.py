from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, Concatenate, Optional, ParamSpec

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


P = ParamSpec("P")

PreWrapFuncT = Callable[Concatenate[typer.Context, P], None]
PostWrapFuncT = Callable[Concatenate[typer.Context, P], None]


class WithBeekeeper(CommonBaseModel):
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option
    beekeeper: "Beekeeper"

    @classmethod
    def decorator(cls, func: PreWrapFuncT[P]) -> PostWrapFuncT[P]:
        common = cls.construct(beekeeper=None)  # type: ignore[arg-type]

        @merge_args(func)
        @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
        def wrapper(
            ctx: typer.Context,
            beekeeper_remote: Optional[str] = common.beekeeper_remote,
            *args: Any,
            **kwargs: Any,
        ) -> None:
            from clive.__private.core.beekeeper import Beekeeper
            from clive.__private.core.exit_call_handler import ExitCallHandler
            from clive.core.url import Url

            beekeeper_remote_endpoint = Url.parse(beekeeper_remote) if beekeeper_remote else None

            cls._print_launching_beekeeper(beekeeper_remote_endpoint)

            with ExitCallHandler(
                Beekeeper(remote_endpoint=beekeeper_remote_endpoint),
                finally_callback=lambda bk: bk.close(),
            ) as beekeeper:
                beekeeper.start()
                ctx.params.update(beekeeper=beekeeper)
                func(ctx, *args, **kwargs)

        return wrapper  # type: ignore[no-any-return]

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.beekeeper import Beekeeper  # noqa: F401

        WithBeekeeper.update_forward_refs(**locals())
