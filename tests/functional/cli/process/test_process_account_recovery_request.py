from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.keys.keys import PublicKey
from clive.__private.models.schemas import Authority, RequestAccountRecoveryOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.testnet_block_log.constants import CREATOR_ACCOUNT, WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


INITMINER_KEY_ALIAS: Final[str] = "initminer_key"
BOB_KEY_ALIAS: Final[str] = "bob_key"


async def test_request_account_recovery(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    new_owner_account = tt.Account("new-owner")
    new_owner_public_key = PublicKey(value=new_owner_account.public_key)

    cli_tester.configure_key_add(key=CREATOR_ACCOUNT.private_key, alias=INITMINER_KEY_ALIAS)

    operation = RequestAccountRecoveryOperation(
        recovery_account=CREATOR_ACCOUNT.name,
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_owner_authority=Authority(
            weight_threshold=1,
            account_auths=[],
            key_auths=[(new_owner_public_key.value, 1)],
        ),
    )

    # ACT
    result = cli_tester.process_request_account_recovery(
        recovery_account=CREATOR_ACCOUNT.name,
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_owner_key=new_owner_public_key.value,
        sign_with=INITMINER_KEY_ALIAS,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_request_account_recovery_by_non_recovery_account(cli_tester: CLITester) -> None:
    # ARRANGE
    new_owner_account = tt.Account("new-owner")
    new_owner_public_key = PublicKey(value=new_owner_account.public_key)

    bob = WATCHED_ACCOUNTS_DATA[0].account
    cli_tester.configure_key_add(key=bob.private_key, alias=BOB_KEY_ALIAS)

    # ACT & ASSERT
    with pytest.raises(CLITestCommandError):
        cli_tester.process_request_account_recovery(
            recovery_account=bob.name,
            account_to_recover=WORKING_ACCOUNT_NAME,
            new_owner_key=new_owner_public_key.value,
            sign_with=BOB_KEY_ALIAS,
        )
