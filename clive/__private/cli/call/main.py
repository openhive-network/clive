from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters.argument_related_options import _make_argument_related_option
from clive.__private.cli.common.parameters.argument_related_options import (
    account_name as account_name_argument_related_option,
)
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue
from clive.__private.cli.common.parameters.styling import stylized_help
from clive.__private.core.types import AuthorityLevel
from clive.__private.core.formatters.case import dasherize, underscore
from beekeepy.handle.remote import AbstractAsyncApi

call = CliveTyper(name="call", help="Invoke api methods.")

def append_method_to_typer(api_typer, api_name: str, method_name: str) -> None:
    method_name_ = dasherize(method_name)
    @api_typer.command(name=method_name_)
    async def api(
        api_params: list[str] | None = typer.Argument(
            None,
            help="arg-name=arg-value pairs for the api method",
        ),
    ) -> None:
        from clive.__private.cli.commands.call.call import Call  # noqa: PLC0415

        await Call(
            api_name=api_name,
            function_name=method_name,
            api_params=api_params if api_params is not None else [],
        ).run()
    api.__doc__ = f"for {api_name}.{method_name}"


def create_typer_for_api(api_name: str, api_object: AbstractAsyncApi) -> typer.Typer:
    api_name_ = dasherize(api_name)
    api_typer = CliveTyper(name=dasherize(api_name_), help=f"Invoke {api_name_}_api methods.")
    

    methods = api_object._get_registered_methods()[False][api_name]
    for method_name in methods:
        append_method_to_typer(api_typer, api_name, method_name)
    
    return api_typer




import inspect
from clive.__private.core.node import Node
from clive.__private.core.node.async_hived.async_handle import AsyncHived
from clive.__private.core.node.async_hived.api.api_collection import HivedAsyncApiCollection
from clive.__private.core.node.async_hived.api.database_api import AsyncDatabaseApi
from clive.__private.settings import safe_settings
settings = safe_settings.node.settings_factory("http:127.0.0.1:8090")
async_hived = AsyncHived(settings=settings)
api = async_hived.api
apis = {name: value for name, value in inspect.getmembers(api) if "_api" in name}

for api_name, api_object in apis.items():
    api_typer = create_typer_for_api(api_name, api_object)
    call.add_typer(api_typer)

