from __future__ import annotations

import errno
import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import msgspec

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.abc.node_address_cli_command import NodeAddressCLICommand
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperRemoteAddressIsNotSetError,
    CLIBeekeeperSessionTokenNotSetError,
    CLINoProfileUnlockedError,
    CLIPrettyError,
)
from clive.__private.cli.print_cli import print_json
from clive.__private.core.formatters.case import camelize
from clive.__private.models.schemas import DecodeError, JsonString, ValidationError

if TYPE_CHECKING:
    from typing import Any

    from wax import IHiveChainInterface


def get_api_class_name(api_name: str) -> str:
    return camelize(api_name)


def get_api_client_module_path(api_name: str) -> str:
    return f"{api_name}.{api_name}_client"


class CLICallAPINoNodeAddressError(CLIPrettyError):
    """Raise when no node address is provided and there is no unlocked profile."""

    def __init__(self) -> None:
        super().__init__(
            "Option '--node-address' must be provided or profile must be unlocked to load configured node address.",
            errno.EINVAL,
        )


class CLICallAPIPackageNotFoundError(CLIPrettyError):
    """
    Raise when api package for requested api is not installed.

    Args:
        api_name: Requested api that was not found.
    """

    def __init__(self, api_name: str) -> None:
        message = f"Package for api `{api_name}` not found."
        super().__init__(message, errno.EINVAL)


class CLICallAPIClientModuleNotFoundError(CLIPrettyError):
    """
    Raise when client module in requested api was not found.

    Args:
        api_client_module_name: Requested client module that was not found.
        api_name: Requested api.
    """

    def __init__(self, api_client_module_name: str, api_name: str) -> None:
        message = (
            f"Module `{api_client_module_name}` for api `{api_name}` not found. "
            f"This might be a problem with installed `{api_name}`."
        )
        super().__init__(message, errno.EINVAL)


class CLICallAPIClassDefinitionNotFoundError(CLIPrettyError):
    """
    Raise when in client module there was not found api class definition.

    Args:
        api_class_name: Requested api definition class that was not found.
        api_name: Requested api.
    """

    def __init__(self, api_class_name: str, api_name: str) -> None:
        message = (
            f"Api class `{api_class_name}` for api `{api_name}` not found. "
            f"This might be a problem with installed `{api_name}`."
        )
        super().__init__(message, errno.EINVAL)


class CLICallAPIMethodNotFoundError(CLIPrettyError):
    """
    Raise when api package is installed but requested method was not found.

    Args:
        method_name: Requested api method that was not found.
        api_name: Requested api.
    """

    def __init__(self, method_name: str, api_name: str) -> None:
        message = (
            f"No method `{method_name}` found in api `{api_name}`. This might be a problem with installed `{api_name}`."
        )
        super().__init__(message, errno.EINVAL)


class CLICallAPIParamNotAJSONContainerError(CLIPrettyError):
    """
    Raise when passed parameters are not dict or list.

    Args:
        raw_params: Parameters before parsing.
    """

    def __init__(self, raw_params: str) -> None:
        message = f"Params must be a json string representing a dict ('{{..}}'). Received `{raw_params}`"
        super().__init__(message, errno.EINVAL)


@dataclass(kw_only=True)
class _CallAPICommon(ExternalCLICommand, ABC):
    """
    Common data and logic shared between CallAPIUseProfile and CallAPIUseNodeAddress.

    Attributes:
        api_name: The name of the API to call (e.g., "database_api", "block_api").
        method_name: The name of the method to call on the API.
        params: JSON string containing the parameters to pass to the API method.
    """

    api_name: str
    method_name: str
    params: str
    _api_class: type = field(init=False)
    _parsed_params: dict[str, Any] = field(init=False)

    @property
    @abstractmethod
    def wax_interface(self) -> IHiveChainInterface:
        """Return the wax interface to use for API calls."""

    def build_extended_api_collection(self) -> type:
        api_name = self.api_name
        api_class = self._api_class

        class RequestedApiCollection:
            def __init__(self) -> None:
                setattr(self, api_name, api_class)

        return RequestedApiCollection

    async def call_api_and_print_result(self) -> None:
        collection_type = self.build_extended_api_collection()
        extended_chain = self.wax_interface.extends(collection_type)

        api_instance = getattr(extended_chain.api, self.api_name)
        api_method_awaitable = getattr(api_instance, self.method_name)

        # currently we don't support condenser_api
        result = await api_method_awaitable(**self.get_keyword_params())

        print_json(msgspec.json.encode(result).decode())

    def get_keyword_params(self) -> dict[str, Any]:
        return self._parsed_params

    async def validate(self) -> None:
        self.validate_api_call()
        await super().validate()

    def validate_api_call(self) -> None:
        self._validate_api_name()
        self._validate_api_method_name()
        self._validate_api_call_params()

    async def _run(self) -> None:
        await self.call_api_and_print_result()

    def _validate_api_call_params(self) -> None:
        try:
            self._parsed_params = JsonString(self.params).value
        except (DecodeError, ValidationError) as err:
            raise CLICallAPIParamNotAJSONContainerError(self.params) from err
        if not isinstance(self._parsed_params, dict):
            raise CLICallAPIParamNotAJSONContainerError(self.params)

    def _validate_api_method_name(self) -> None:
        if not hasattr(self._api_class, self.method_name):
            raise CLICallAPIMethodNotFoundError(self.method_name, self.api_name)

    def _validate_api_name(self) -> None:
        api_client_module_name = get_api_client_module_path(self.api_name)
        api_class_name = get_api_class_name(self.api_name)
        try:
            importlib.import_module(self.api_name)
        except Exception as err:
            raise CLICallAPIPackageNotFoundError(self.api_name) from err
        try:
            client_module = importlib.import_module(api_client_module_name)
        except Exception as err:
            raise CLICallAPIClientModuleNotFoundError(api_client_module_name, self.api_name) from err
        try:
            api_class = getattr(client_module, api_class_name)
        except Exception as err:
            raise CLICallAPIClassDefinitionNotFoundError(api_class_name, self.api_name) from err
        self._api_class = api_class


@dataclass(kw_only=True)
class CallAPIUseProfile(_CallAPICommon, WorldBasedCommand):
    """Call API method using node address from the unlocked profile."""

    @property
    def wax_interface(self) -> IHiveChainInterface:
        return self.world.wax_interface

    async def run(self) -> None:
        try:
            await super().run()
        except (
            CLIBeekeeperRemoteAddressIsNotSetError,
            CLIBeekeeperSessionTokenNotSetError,
            CLINoProfileUnlockedError,
        ) as err:
            raise CLICallAPINoNodeAddressError from err

    def _print_launching_beekeeper(self) -> None:
        """Override WorldBasedCommand implementation so this command prints only raw json."""


@dataclass(kw_only=True)
class CallAPIUseNodeAddress(_CallAPICommon, NodeAddressCLICommand):
    """Call API method using explicitly provided node address."""

    @property
    def wax_interface(self) -> IHiveChainInterface:
        return self._build_wax_interface()
