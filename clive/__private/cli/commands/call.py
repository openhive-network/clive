from __future__ import annotations

import importlib
from dataclasses import dataclass, field

import msgspec

from beekeepy.communication import AioHttpCommunicator
from beekeepy.communication import Callbacks, CommunicationSettings
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.cli.print_cli import print_json, print_cli
from clive.__private.core.formatters.case import camelize
from clive.__private.models.schemas import CustomJsonOperation, JsonString
from beekeepy._utilities.build_json_rpc_call import build_json_rpc_call


@dataclass(kw_only=True)
class Call(WorldBasedCommand):
    api_name: str
    method_name: str
    params: str
    _json_params: list | dict = field(init=False)

    async def _run(self) -> None:


        url = self.world.node.http_endpoint
        endpoint = f"{self.api_name}.{self.method_name}"
        data = build_json_rpc_call(
            method=endpoint,
            params=self.params,
            id_=0,
        )
        communicator = AioHttpCommunicator(settings=CommunicationSettings())
        response = await communicator.async_post(url, data)
        breakpoint()
        print_cli(response)

    async def _hook_before_entering_context_manager(self) -> None:
        """Overrides WorldBasedCommand implementation so this command prints only raw json."""
        return

    async def validate(self) -> None:
        self._validate_api_name()
        self._validate_method_name()
        self._validate_params()
        await super().validate()

    def _validate_api_name(self) -> None:
        try:
            importlib.import_module(self.api_name)
        except ModuleNotFoundError as err:
            raise CLIPrettyError(f"Package for api `{self.api_name}` not found.") from err

    def _validate_method_name(self) -> None:
        pass

    def _validate_params(self) -> None:
        self._parse_params()

    def _get_positional_params(self) -> list:
        return self._json_params if isinstance(self._json_params, list) else []

    def _get_keyword_params(self) -> dict:
        return self._json_params if isinstance(self._json_params, dict) else {}

    def _parse_params(self) -> None:
        try:
            json_params = JsonString(self.params).value
        except msgspec.DecodeError as err:
            raise CLIPrettyError(f"Params is not a valid json string! Received `{self.params}`") from err
        self._json_params = json_params
        if not isinstance(self._json_params, (list, dict)):
            raise CLIPrettyError(
                f"Params must be a json string representing a list or a dict! Received `{self.params}`"
            )
