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
    from typing import Callable, Awaitable, Any

@dataclass(kw_only=True)
class Call(WorldBasedCommand):
    api_name: str
    function_name: str
    api_params: list[str]
    async def _hook_before_entering_context_manager(self) -> None:
        pass

    async def _run(self) -> None:
        if "help" in self.api_params:
            print_cli("Help option detected")
            return
        awaitable=self._get_awaitable()
        params_dict = self._parse_api_params()
        response = await awaitable(**params_dict)
        print_cli(response.json())

    def _parse_api_params(self) -> dict[str, Any]:
        params_dict: dict[str, Any] = {}
        for param in self.api_params:
            param_name, param_value = param.split("=", 1) if "=" in param else (param, True)
            arg_name_underscore = underscore(param_name)
            params_dict[arg_name_underscore] = param_value
        return params_dict
    
    def _get_awaitable(self) -> Awaitable:
        api_name = underscore(self.api_name).removesuffix("_api")
        function_name = underscore(self.function_name)  
        api = getattr(self.world.node.api, api_name)
        method = getattr(api, function_name)
        return method