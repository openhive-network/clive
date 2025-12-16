from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.commands.call_api import (
    CLICallAPIMethodNotFoundError,
    CLICallAPINoNodeAddressError,
    CLICallAPIPackageNotFoundError,
    CLICallAPIParamNotAJSONContainerError,
)
from clive_local_tools.cli.checkers import assert_result_contains_valid_json
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import HIVED_API_NAMES
from clive_local_tools.helpers import create_transaction_filepath, get_formatted_error_message
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

FAILING_API: Final[tuple[str, ...]] = (
    "database_api.get_config",
    "database_api.get_version",
    "debug_node_api.debug_get_head_block",
)


@dataclass
class ApiMethodInfo:
    api_name: str
    method_name: str
    are_params_required: bool

    def __str__(self) -> str:
        return f"{self.api_name}.{self.method_name}"


def list_api_method_info() -> list[ApiMethodInfo]:
    result: list[ApiMethodInfo] = []
    for api_name in HIVED_API_NAMES:
        module = importlib.import_module(f"{api_name}.{api_name}_description")
        description = getattr(module, f"{api_name}_description")
        for api_method_name in description[api_name]:
            are_params_required: bool = description[api_name][api_method_name]["params"] is not None
            info = ApiMethodInfo(api_name, api_method_name, are_params_required)
            if str(info) in FAILING_API:
                continue
            result.append(ApiMethodInfo(api_name, api_method_name, are_params_required))
    return result


@pytest.mark.parametrize(
    "api_method_info",
    [pytest.param(info, id=str(info)) for info in list_api_method_info() if not info.are_params_required],
)
def test_call_methods_no_params(cli_tester: CLITester, api_method_info: ApiMethodInfo) -> None:
    """Should call api method and give json as command stdout."""
    # ARRANGE
    api_name = api_method_info.api_name
    method_name = api_method_info.method_name

    # ACT
    result = cli_tester.call(api_name, method_name)

    # ASSERT
    assert_result_contains_valid_json(result)


@pytest.mark.parametrize(
    ("api_name", "method_name", "params"),
    [
        # remove xfail after block_api get_block return fix in generated api packages
        pytest.param("block_api", "get_block", '{"block_num": 10}', marks=pytest.mark.xfail),
        pytest.param("block_api", "get_block", '{"block_num": "10"}', marks=pytest.mark.xfail),
        ("account_history_api", "get_ops_in_block", None),
        ("account_history_api", "get_ops_in_block", "{}"),
        ("account_history_api", "get_ops_in_block", '{"block_num": 10}'),
        ("account_history_api", "get_ops_in_block", '{"block_num": "10"}'),
        ("account_history_api", "get_ops_in_block", '{"block_num": 10, "only_virtual": true}'),
        ("account_history_api", "get_ops_in_block", '{"block_num": 10, "include_reversible": true}'),
        ("database_api", "get_feed_history", None),
        ("database_api", "get_active_witnesses", None),
        ("database_api", "get_active_witnesses", '{"include_future": true}'),
    ],
)
def test_common_api_calls(cli_tester: CLITester, api_name: str, method_name: str, params: str | None) -> None:
    # ACT
    result = (
        cli_tester.call(api_name, method_name, params) if params is not None else cli_tester.call(api_name, method_name)
    )

    # ASSERT
    assert_result_contains_valid_json(result)


def test_broadcast_transaction(cli_tester: CLITester) -> None:
    """Test broadcasting a transaction with complex parameters."""
    # ARRANGE
    api_name = "network_broadcast_api"
    method_name = "broadcast_transaction"
    memo = '"' + '"' + "\\" + '"' + "\\" + "'" + "\\" + "\\"  # after escaping ""\"\'\\
    transaction_filepath = create_transaction_filepath()
    cli_tester.process_transfer(
        to=WORKING_ACCOUNT_NAME, amount=tt.Asset.Hive(1), memo=memo, save_file=transaction_filepath
    )
    with transaction_filepath.open() as saved_transaction:
        params = '{"trx": ' + str(saved_transaction.read()) + "}"

    # ACT & ASSERT
    cli_tester.call(api_name, method_name, params)


def test_call_locked(cli_tester_locked: CLITester, node: tt.RawNode) -> None:
    """Test call api when locked and custom node address must be set."""
    # ARRANGE
    api_name = "database_api"
    method_name = "get_dynamic_global_properties"

    # ACT
    result = cli_tester_locked.call(api_name, method_name, node_address=str(node.http_endpoint))

    # ASSERT
    assert_result_contains_valid_json(result)


@pytest.mark.parametrize(
    ("cli_tester_variant"),
    ["locked", "without remote address", "without session token"],
    indirect=["cli_tester_variant"],
)
def test_negative_call_locked_without_node_address(cli_tester_variant: CLITester) -> None:
    # ARRANGE
    api_name = "database_api"
    method_name = "get_dynamic_global_properties"
    expected_error = get_formatted_error_message(CLICallAPINoNodeAddressError())

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester_variant.call(api_name, method_name)


def test_negative_invalid_api_name(cli_tester: CLITester) -> None:
    # ARRANGE
    invalid_api_name = "database-api"
    method_name = "get-dynamic-global-properties"
    expected_error = get_formatted_error_message(CLICallAPIPackageNotFoundError(invalid_api_name))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.call(invalid_api_name, method_name)


def test_negative_invalid_method_name(cli_tester: CLITester) -> None:
    # ARRANGE
    api_name = "database_api"
    invalid_method_name = "get-dynamic-global-properties"
    expected_error = get_formatted_error_message(CLICallAPIMethodNotFoundError(invalid_method_name, api_name))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.call(api_name, invalid_method_name)


def test_negative_invalid_params_decode(cli_tester: CLITester) -> None:
    """Params are not valid json."""
    # ARRANGE
    raw_params = "{"  # invalid json
    expected_error = get_formatted_error_message(CLICallAPIParamNotAJSONContainerError(raw_params))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.call("database_api", "get_dynamic_global_properties", raw_params)


def test_negative_invalid_params_format(cli_tester: CLITester) -> None:
    """Params are valid json but we expect dict or list."""
    # ARRANGE
    raw_params = '""'  # valid json but not a container
    expected_error = get_formatted_error_message(CLICallAPIParamNotAJSONContainerError(raw_params))

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=expected_error):
        cli_tester.call("database_api", "get_dynamic_global_properties", raw_params)
