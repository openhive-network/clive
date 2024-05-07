from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.core.keys.keys import PrivateKeyAliased
from clive_local_tools.cli.checkers import assert_exit_code, assert_new_account_tokens
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.cli.helpers import get_account_creation_fee
from clive_local_tools.data.constants import (
    ALT_WORKING_ACCOUNT1_KEY_ALIAS,
    EMPTY_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_KEY_ALIAS,
    WORKING_ACCOUNT_PASSWORD,
)
from clive_local_tools.testnet_block_log import ALT_WORKING_ACCOUNT1_DATA, EMPTY_ACCOUNT, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.fixture()
async def prepare_beekeeper_wallet(world: World) -> None:
    async with world:
        password = (await world.commands.create_wallet(password=WORKING_ACCOUNT_PASSWORD)).result_or_raise
        tt.logger.info(f"password for {WORKING_ACCOUNT_DATA.account.name} is: `{password}`")

        world.profile_data.keys.add_to_import(
            PrivateKeyAliased(value=WORKING_ACCOUNT_DATA.account.private_key, alias=f"{WORKING_ACCOUNT_KEY_ALIAS}"),
            PrivateKeyAliased(
                value=ALT_WORKING_ACCOUNT1_DATA.account.private_key, alias=f"{ALT_WORKING_ACCOUNT1_KEY_ALIAS}"
            ),
            PrivateKeyAliased(value=EMPTY_ACCOUNT.private_key, alias=f"{EMPTY_ACCOUNT_KEY_ALIAS}"),
        )
        await world.commands.sync_data_with_beekeeper()


async def test_pay_with_rc(cli_tester: CLITester) -> None:
    # ARRNGE
    # ACT
    cli_tester.process_claim_new_account_token(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ASSERT
    assert_new_account_tokens(cli_tester, tokens_amount=1)


async def test_pay_with_hive(cli_tester: CLITester) -> None:
    # ARRNGE
    correct_fee = get_account_creation_fee(cli_tester)

    # ACT
    cli_tester.process_claim_new_account_token(
        password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, fee=correct_fee
    )

    # ASSERT
    assert_new_account_tokens(cli_tester, tokens_amount=1)


async def test_cant_pay_more(cli_tester: CLITester) -> None:
    # ARRNGE
    higher_fee = get_account_creation_fee(cli_tester) + 1
    expected_error = "Cannot pay more than account creation fee."

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as claim_new_account_token_exception_info:
        cli_tester.process_claim_new_account_token(
            password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, fee=higher_fee
        )

    # ASSERT
    assert_exit_code(claim_new_account_token_exception_info, 1)
    assert_new_account_tokens(cli_tester, tokens_amount=0)


async def test_cant_pay_less(cli_tester: CLITester) -> None:
    # ARRNGE
    smaller_fee = get_account_creation_fee(cli_tester) + 1
    expected_error = "Cannot pay more than account creation fee."

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as claim_new_account_token_exception_info:
        cli_tester.process_claim_new_account_token(
            password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS, fee=smaller_fee
        )

    # ASSERT
    assert_exit_code(claim_new_account_token_exception_info, 1)
    assert_new_account_tokens(cli_tester, tokens_amount=0)


async def test_not_enough_hive(cli_tester: CLITester) -> None:
    # ARRNGE
    correct_fee = get_account_creation_fee(cli_tester)
    expected_error = "Insufficient balance to create account."

    # ACT
    with pytest.raises(CLITestCommandError, match=expected_error) as claim_new_account_token_exception_info:
        cli_tester.process_claim_new_account_token(
            password=WORKING_ACCOUNT_PASSWORD,
            sign=EMPTY_ACCOUNT_KEY_ALIAS,
            fee=correct_fee,
            creator=EMPTY_ACCOUNT.name,
        )

    # ASSERT
    assert_exit_code(claim_new_account_token_exception_info, 1)
    assert_new_account_tokens(cli_tester, tokens_amount=0)
