from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from json import loads, JSONDecodeError
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.cli.exceptions import CLIMutuallyExclusiveOptionsError
from clive.__private.core.formatters.case import camelize
from clive.__private.models.schemas import TransferOperation
from clive_local_tools.data.constants import API_NAMES
from clive_local_tools.checkers.blockchain_checkers import (
    assert_transaction_in_blockchain,
    assert_transaction_not_in_blockchain,
)
from clive_local_tools.cli.checkers import (
    assert_contains_dry_run_message,
    assert_contains_transaction_broadcasted_message,
    assert_contains_transaction_saved_to_file_message,
    assert_does_not_contain_transaction_broadcasted_message,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import create_transaction_file, create_transaction_filepath
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)

type ApiMethodInfo = tuple[str, str]
@dataclass
class ApiMethodInfo:
    api_name: str
    method_name: str

    def __repr__(self) -> str:
        return f"{self.api_name}.{self.method_name}"


def list_apis_and_methods() -> list[tuple[str, str, bool]]:
    result = []
    for api_name in API_NAMES:
        module = importlib.import_module(f"{api_name}.{api_name}_description")
        description = getattr(module, f"{api_name}_description")
        for method_name in description[api_name].keys():
            are_params_required: bool = description[api_name][method_name]["params"] is not None
            result.append((api_name, method_name, are_params_required))
    return result


def list_apis_and_methods_no_params() -> list[ApiMethodInfo]:
    return [ApiMethodInfo(api_name, method_name) for api_name, method_name, are_params_required in list_apis_and_methods() if not are_params_required]



def list_apis_and_methods_with_params() -> list[ApiMethodInfo]:
    return [ApiMethodInfo(api_name, method_name) for api_name, method_name, are_params_required in list_apis_and_methods() if are_params_required]


@pytest.mark.parametrize( "api_method_info", [pytest.param(item, id=repr(item)) for item in list_apis_and_methods_no_params()])
def test_call_methods_no_params(cli_tester: CLITester, api_method_info: ApiMethodInfo) -> None:
    """Should call api method and give json as command stdout."""
    # ARRANGE
    api_name = api_method_info.api_name
    method_name = api_method_info.method_name

    # ACT
    result = cli_tester.call(api_name, method_name)

    # ASSERT
    try:
        loads(result.stdout)
    except JSONDecodeError:
        pytest.fail(f"Expected valid JSON response from api.\n{result.info}")


@pytest.mark.parametrize("api_method_info", [pytest.param(item, id=repr(item)) for item in list_apis_and_methods_with_params()])
def test_call_methods_with_params(cli_tester: CLITester, api_method_info: ApiMethodInfo) -> None:
    """Should call api method and raise exception about missing params."""
    # ARRANGE
    api_name = api_method_info.api_name
    method_name = api_method_info.method_name

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError):
        cli_tester.call(api_name, method_name)
