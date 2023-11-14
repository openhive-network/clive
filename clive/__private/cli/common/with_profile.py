from functools import wraps

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.core._async import asyncio_run


class WithProfile(CommonBaseModel):
    profile_name: str

    @classmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        @merge_args(func)
        @wraps(func)
        def wrapper(
            ctx: typer.Context,
            profile_name: str = options.profile_name_option,  # noqa: ARG001
            **kwargs: DecoratorParams.kwargs,
        ) -> None:
            asyncio_run(func(ctx, **kwargs))

        return wrapper  # type: ignore[no-any-return]
