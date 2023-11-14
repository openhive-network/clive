from functools import wraps
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.core._async import asyncio_run


class OperationCommon(CommonBaseModel):
    profile_name: str
    password: Optional[str]
    sign: Optional[str]
    beekeeper_remote: Optional[str]
    broadcast: bool
    save_file: Optional[str]

    @classmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        @merge_args(func)
        @wraps(func)
        def wrapper(
            ctx: typer.Context,
            profile_name: str = options.profile_name_option,  # noqa: ARG001
            password: Optional[str] = options.password_optional_option,  # noqa: ARG001
            sign: Optional[str] = typer.Option(  # noqa: ARG001
                None, help="Key alias to sign the transaction with.", show_default=False
            ),
            beekeeper_remote: Optional[str] = options.beekeeper_remote_option,  # noqa: ARG001
            broadcast: bool = typer.Option(  # noqa: ARG001
                True, help="Whether broadcast the transaction. (i.e. dry-run)"
            ),
            save_file: Optional[str] = typer.Option(  # noqa: ARG001
                None,
                help="The file to save the transaction to (format is determined by file extension - .bin or .json).",
                show_default=False,
            ),
            **kwargs: Any,
        ) -> None:
            asyncio_run(func(ctx, **kwargs))

        return wrapper  # type: ignore[no-any-return]
