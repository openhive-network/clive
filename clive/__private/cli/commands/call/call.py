from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beekeepy.communication import AioHttpCommunicator
from beekeepy.communication import Callbacks, CommunicationSettings
from beekeepy._utilities.build_json_rpc_call import build_json_rpc_call

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.keys import PrivateKey
from clive.__private.core.formatters.case import underscore

if TYPE_CHECKING:
    from typing import Callable

@dataclass(kw_only=True)
class Call(WorldBasedCommand):
    api_name: str
    function_name: str
    api_params: list[str]

    async def _run(self) -> None:
        if "help" in self.api_params:
            print_cli("Help option detected")
            return
        method=self._get_jsonrpc_method()
        params = self._get_jsonrpc_params()
        data = build_json_rpc_call(method=method, params=params)
        communicator = AioHttpCommunicator(settings=CommunicationSettings())
        url = self.world.node.http_endpoint
        response = await communicator.async_post(url, data)
        print_cli(response)

    def _get_jsonrpc_params(self) -> str:
        params_dict: dict[str, str] = {}
        for param in self.api_params:
            param_name, param_value = param.split("=", 1) if "=" in param else (param, "true")
            arg_name_underscore = underscore(param_name)
            params_dict[arg_name_underscore] = param_value
        params_string = ", ".join(f'"{key}": "{value}"' for key, value in params_dict.items())
        return "{" + params_string + "}"
    
    def _get_jsonrpc_method(self) -> str:
        api_name_underscore = underscore(self.api_name)
        function_name_underscore = underscore(self.function_name)
        return f"{api_name_underscore}.{function_name_underscore}"
