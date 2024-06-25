from __future__ import annotations

import errno
from typing import TYPE_CHECKING, Final
from uuid import uuid4

import pytest

from clive_local_tools.cli import checkers
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


EXAMPLE_OBJECT: Final[str] = '{"foo": "bar"}'
EXAMPLE_STRING: Final[str] = '"somestring"'
EXAMPLE_NUMBER: Final[str] = "123456.789"
INVALID_JSON: Final[str] = '{"foo":'
EXAMPLE_FILE_RELATIVE_PATH: Final[str] = "test_file.json"
TRANSACTION_RELATIVE_PATH: Final[str] = "full_trx.json"
OTHER_ACCOUNT: Final[tt.Account] = EMPTY_ACCOUNT


def generate_random_id() -> str:
    return uuid4().hex


@pytest.mark.parametrize("json_", [EXAMPLE_OBJECT, EXAMPLE_STRING, EXAMPLE_NUMBER])
async def test_authorize_default(cli_tester: CLITester, json_: str) -> None:
    # ACT
    cli_tester.process_custom_json(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, id_=generate_random_id(), json_=json_
    )


async def test_authorize_posting(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_custom_json(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        authorize=WORKING_ACCOUNT_DATA.account.name,
        id_=generate_random_id(),
        json_=EXAMPLE_OBJECT,
    )


async def test_authorize_multiple_posting(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_custom_json(
        broadcast=False,
        authorize=[WORKING_ACCOUNT_DATA.account.name, OTHER_ACCOUNT.name],
        id_=generate_random_id(),
        json_=EXAMPLE_OBJECT,
    )


async def test_authorize_active(cli_tester: CLITester) -> None:
    # ACT
    cli_tester.process_custom_json(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        authorize_by_active=WORKING_ACCOUNT_DATA.account.name,
        id_=generate_random_id(),
        json_=EXAMPLE_OBJECT,
    )


async def test_json_as_file(cli_tester: CLITester, tmp_path: Path) -> None:
    # ARRANGE
    json_file = tmp_path / EXAMPLE_FILE_RELATIVE_PATH
    json_file.write_text(EXAMPLE_OBJECT)

    # ACT
    cli_tester.process_custom_json(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        authorize=WORKING_ACCOUNT_DATA.account.name,
        id_=generate_random_id(),
        json_=json_file,
    )


async def test_negative_invalid_json_format(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "The input is neither a valid JSON string nor a valid file path."

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as exception_info:
        cli_tester.process_custom_json(
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            authorize=WORKING_ACCOUNT_DATA.account.name,
            id_=generate_random_id(),
            json_=INVALID_JSON,
        )

    # ASSERT
    checkers.assert_exit_code(exception_info, errno.EINVAL)


async def test_negative_active_and_posting_auths(cli_tester: CLITester) -> None:
    # ARRANGE
    expected_error = "Transaction can't be signed by posting and active authority"

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as exception_info:
        (
            cli_tester.process_custom_json(
                broadcast=False,
                authorize_by_active=OTHER_ACCOUNT.name,
                authorize=WORKING_ACCOUNT_DATA.account.name,
                id_=generate_random_id(),
                json_=EXAMPLE_OBJECT,
            )
        )

    # ASSERT
    checkers.assert_exit_code(exception_info, errno.EINVAL)


async def test_negative_invalid_json_file_path(cli_tester: CLITester, tmp_path: Path) -> None:
    # ARRANGE
    expected_error = "The input is neither a valid JSON string nor a valid file path."
    invalid_path = tmp_path / EXAMPLE_FILE_RELATIVE_PATH
    assert not invalid_path.exists()

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as exception_info:
        cli_tester.process_custom_json(
            password=WORKING_ACCOUNT_PASSWORD,
            sign=WORKING_ACCOUNT_KEY_ALIAS,
            id_=generate_random_id(),
            json_=invalid_path,
        )

    # ASSERT
    checkers.assert_exit_code(exception_info, errno.EINVAL)


@pytest.mark.parametrize("json_", [EXAMPLE_OBJECT, EXAMPLE_STRING, EXAMPLE_NUMBER])
async def test_load_transaction_from_file(cli_tester: CLITester, tmp_path: Path, json_: str) -> None:
    # ARRANGE
    trx_file = tmp_path / TRANSACTION_RELATIVE_PATH
    cli_tester.process_custom_json(
        authorize=WORKING_ACCOUNT_DATA.account.name,
        id_=generate_random_id(),
        json_=json_,
        broadcast=False,
        save_file=trx_file,
    )

    # ACT
    # ASSERT
    cli_tester.process_transaction(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        already_signed_mode="multisign",
        from_file=trx_file,
    )
