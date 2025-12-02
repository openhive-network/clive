from __future__ import annotations

import errno
import importlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import msgspec

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperRemoteAddressIsNotSetError,
    CLIBeekeeperSessionTokenNotSetError,
    CLINoProfileUnlockedError,
    CLIPrettyError,
)
from clive.__private.cli.print_cli import print_json
from clive.__private.core.constants.setting_identifiers import NODE_CHAIN_ID
from clive.__private.core.formatters.case import camelize
from clive.__private.models.schemas import DecodeError, JsonString, ValidationError
from clive.__private.settings import clive_prefixed_envvar, safe_settings
from wax.wax_factory import create_hive_chain
from wax.wax_options import WaxChainOptions

if TYPE_CHECKING:
    from typing import Any

    from wax import IHiveChainInterface
    from wax.api.collection import WaxApiCollection
    from wax.interfaces import ExtendedApiCollectionT


def get_api_class_name(api_name: str) -> str:
    return f"{camelize(api_name)}"


def get_api_client_module_path(api_name: str) -> str:
    return f"{api_name}.{api_name}_client"


class CLINoNodeAddressError(CLIPrettyError):
    """Raise when no node address is provided and there is no unlocked profile."""

    def __init__(self) -> None:
        super().__init__(
            "Option '--node-address' must be provided or profile must be unlocked to load configured node address.",
            errno.EINVAL,
        )


class CLIApiPackageNotFoundError(CLIPrettyError):
    """
    Raise when api package for requested api is not installed.

    Args:
        api_name: Requested api that was not found.
    """

    def __init__(self, api_name: str) -> None:
        message = f"Package for api `{api_name}` not found."
        super().__init__(message, errno.EINVAL)


class CLIApiClientModuleNotFoundError(CLIPrettyError):
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


class CLIApiClassDefinitionNotFoundError(CLIPrettyError):
    """
    Raise when in client module there was not found api class definition.

    Args:
        api_class_name: Requested api definition class that was not found.
        api_name: Requested api.
    """

    def __init__(self, api_class_name: str, api_name: str) -> None:
        message = (
            f"No api class `{api_class_name}` for api `{api_name}` not found. "
            f"This might be a problem with installed `{api_name}`."
        )
        super().__init__(message, errno.EINVAL)


class CLIMethodNotFoundError(CLIPrettyError):
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


class CLIParamNotAJSONContainerError(CLIPrettyError):
    """
    Raise when passed parameters are not dict or list.

    Args:
        raw_params: Parameters before parsing.
    """

    def __init__(self, raw_params: str) -> None:
        message = (
            "Params must be a json string representing a list ('[..]') or a dict ('{..}') "
            f"depending on the API method. Received `{raw_params}`"
        )
        super().__init__(message, errno.EINVAL)


@dataclass(kw_only=True)
class CallAPI(WorldBasedCommand):
    api_name: str
    method_name: str
    params: str
    node_address: str | None
    _api_class: type = field(init=False)
    _parsed_params: list[Any] | dict[str, Any] = field(init=False)

    @property
    def should_require_unlocked_wallet(self) -> bool:
        return self.use_profile_node_address

    @property
    def should_validate_if_remote_address_required(self) -> bool:
        return self.use_profile_node_address

    @property
    def should_validate_if_session_token_required(self) -> bool:
        return self.use_profile_node_address

    @property
    def use_profile_node_address(self) -> bool:
        return not self.is_option_given(self.node_address)

    async def run(self) -> None:
        try:
            await super().run()
        except (
            CLIBeekeeperRemoteAddressIsNotSetError,
            CLIBeekeeperSessionTokenNotSetError,
            CLINoProfileUnlockedError,
        ) as err:
            raise CLINoNodeAddressError from err

    async def validate(self) -> None:
        self._validate_api_name()
        self._validate_api_method_name()
        self._validate_api_call_params()
        await super().validate()

    async def _run(self) -> None:
        collection_type = self._build_extended_api_collection()
        extended_chain = self._get_extended_chain(collection_type)

        api_instance = getattr(extended_chain.api, self.api_name)
        api_method_awaitable = getattr(api_instance, self.method_name)

        # currently we don't support condenser_api
        result = await api_method_awaitable(**self._get_keyword_params())

        print_json(msgspec.json.encode(result).decode())

    def _build_extended_api_collection(self) -> type:
        api_name = self.api_name
        api_class = self._api_class

        class RequestedApiCollection:
            def __init__(self) -> None:
                setattr(self, api_name, api_class)

        return RequestedApiCollection

    def _build_wax_interface(self) -> IHiveChainInterface:
        chain_id = safe_settings.node.chain_id
        if chain_id is None:
            message = (
                "There is no configured chain id in settings."
                f" You can override settings be environment variable {clive_prefixed_envvar(NODE_CHAIN_ID)}"
            )
            raise CLIPrettyError(message, errno.EINVAL)
        assert self.node_address is not None, "Node address should be set by now."
        wax_chain_options = WaxChainOptions(chain_id=chain_id, endpoint_url=self.node_address)
        return create_hive_chain(wax_chain_options)

    def _get_extended_chain(
        self, collection_type: type[ExtendedApiCollectionT]
    ) -> IHiveChainInterface[ExtendedApiCollectionT | WaxApiCollection]:
        if self.use_profile_node_address:
            return self.world.wax_interface.extends(collection_type)
        wax_interface = self._build_wax_interface()
        return wax_interface.extends(collection_type)

    def _get_keyword_params(self) -> dict[str, Any]:
        return self._parsed_params if isinstance(self._parsed_params, dict) else {}

    def _print_launching_beekeeper(self) -> None:
        """Overrides WorldBasedCommand implementation so this command prints only raw json."""
        return

    def _validate_api_call_params(self) -> None:
        try:
            self._parsed_params = JsonString(self.params).value
        except (DecodeError, ValidationError) as err:
            raise CLIParamNotAJSONContainerError(self.params) from err
        if not isinstance(self._parsed_params, (list, dict)):
            raise CLIParamNotAJSONContainerError(self.params)

    def _validate_api_method_name(self) -> None:
        if not hasattr(self._api_class, self.method_name):
            raise CLIMethodNotFoundError(self.method_name, self.api_name)

    def _validate_api_name(self) -> None:
        api_client_module_name = get_api_client_module_path(self.api_name)
        api_class_name = get_api_class_name(self.api_name)
        try:
            importlib.import_module(self.api_name)
        except Exception as err:
            raise CLIApiPackageNotFoundError(self.api_name) from err
        try:
            client_module = importlib.import_module(api_client_module_name)
        except Exception as err:
            raise CLIApiClientModuleNotFoundError(api_client_module_name, self.api_name) from err
        try:
            api_class = getattr(client_module, api_class_name)
        except Exception as err:
            raise CLIApiClassDefinitionNotFoundError(api_class_name, self.api_name) from err
        self._api_class = api_class
