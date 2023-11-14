from functools import wraps
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.core._async import asyncio_run


class WithBeekeeper(CommonBaseModel):
    beekeeper_remote: Optional[str]

    @classmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        @merge_args(func)
        @wraps(func)
        def wrapper(
            ctx: typer.Context,
            beekeeper_remote: Optional[str] = options.beekeeper_remote_option,  # noqa: ARG001
            **kwargs: Any,
        ) -> None:
            return asyncio_run(func(ctx, **kwargs))

        return wrapper  # type: ignore[no-any-return]
