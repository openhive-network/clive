from collections.abc import Callable
from functools import wraps
from typing import Optional

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.cli.common.options import modified_option
from clive.__private.core._async import asyncio_run


class WorldCommonOptions(CommonBaseModel):
    profile_name: str
    beekeeper_remote: Optional[str]
    use_beekeeper: bool

    @classmethod
    def decorator(cls, *, use_beekeeper: bool = True) -> Callable[[PreWrapFunc[DecoratorParams]], PostWrapFunc[DecoratorParams]]:  # type: ignore[override]
        """
        Decorator to be used on commands that need a world.

        The world could be created with a beekeeper or without.
        Beekeeper is launched locally by default, but it is possible to use a remote beekeeper by specifying the
        `beekeeper_remote` argument in the decorated function.

        Args:
        ----
        use_beekeeper: Set this to False when there is no need to use a beekeeper.
        """

        def outer(func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
            @merge_args(func)
            @wraps(func)
            def inner(
                ctx: typer.Context,
                profile_name: str = options.profile_name_option,  # noqa: ARG001
                beekeeper_remote: Optional[str] = modified_option(  # noqa: ARG001
                    options.beekeeper_remote_option, hidden=not use_beekeeper
                ),
                **kwargs: DecoratorParams.kwargs,
            ) -> None:
                ctx.params.update(use_beekeeper=use_beekeeper)
                asyncio_run(func(ctx, **kwargs))

            return inner  # type: ignore[no-any-return]

        return outer
