from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.keys.keys import PrivateKey, PublicKey
from clive.__private.models.schemas import Authority, RecoverAccountOperation
from clive_local_tools.checkers.blockchain_checkers import assert_operations_placed_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log.constants import (
    CREATOR_ACCOUNT,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


INITMINER_KEY_ALIAS: Final[str] = "initminer_key"
RECOVERY_KEY_ALIAS: Final[str] = "recovery_key"


async def test_recover_account(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    attacker_public_key = PrivateKey.generate().calculate_public_key()
    recovery_private_key = PrivateKey.generate()
    recovery_public_key = recovery_private_key.calculate_public_key()
    alice_public_key = PublicKey(value=WORKING_ACCOUNT_DATA.account.public_key)

    cli_tester.configure_key_add(key=CREATOR_ACCOUNT.private_key, alias=INITMINER_KEY_ALIAS)
    cli_tester.configure_key_add(key=recovery_private_key.value, alias=RECOVERY_KEY_ALIAS)

    # Step 1: Attacker changes alice's owner authority from alice_key to attacker_key
    cli_tester.process_update_authority("owner", sign_with=WORKING_ACCOUNT_KEY_ALIAS).add_key(
        key=attacker_public_key.value, weight=1
    ).remove_key(key=WORKING_ACCOUNT_DATA.account.public_key).fire()

    node.wait_number_of_blocks(1)

    # Step 2: Recovery agent requests recovery, proposing recovery_key as new owner
    cli_tester.process_request_account_recovery(
        recovery_account=CREATOR_ACCOUNT.name,
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_owner_key=recovery_public_key.value,
        sign_with=INITMINER_KEY_ALIAS,
    )

    node.wait_number_of_blocks(1)

    operation = RecoverAccountOperation(
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_owner_authority=Authority(
            weight_threshold=1,
            account_auths=[],
            key_auths=[(recovery_public_key.value, 1)],
        ),
        recent_owner_authority=Authority(
            weight_threshold=1,
            account_auths=[],
            key_auths=[(alice_public_key.value, 1)],
        ),
    )

    # ACT
    result = cli_tester.process_recover_account(
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_owner_key=recovery_public_key.value,
        recent_owner_key=alice_public_key.value,
        sign_with=[RECOVERY_KEY_ALIAS, WORKING_ACCOUNT_KEY_ALIAS],
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_recover_account_fails_without_owner_authority_change(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    recovery_private_key = PrivateKey.generate()
    recovery_public_key = recovery_private_key.calculate_public_key()
    alice_public_key = PublicKey(value=WORKING_ACCOUNT_DATA.account.public_key)

    cli_tester.configure_key_add(key=CREATOR_ACCOUNT.private_key, alias=INITMINER_KEY_ALIAS)
    cli_tester.configure_key_add(key=recovery_private_key.value, alias=RECOVERY_KEY_ALIAS)

    # Initminer requests recovery proposing recovery_key as new owner (this succeeds)
    cli_tester.process_request_account_recovery(
        recovery_account=CREATOR_ACCOUNT.name,
        account_to_recover=WORKING_ACCOUNT_NAME,
        new_owner_key=recovery_public_key.value,
        sign_with=INITMINER_KEY_ALIAS,
    )

    node.wait_number_of_blocks(1)

    # ACT & ASSERT - fails because alice never changed her owner key
    with pytest.raises(CLITestCommandError, match=r"Recent authority not found in authority history\."):
        cli_tester.process_recover_account(
            account_to_recover=WORKING_ACCOUNT_NAME,
            new_owner_key=recovery_public_key.value,
            recent_owner_key=alice_public_key.value,
            sign_with=[RECOVERY_KEY_ALIAS, WORKING_ACCOUNT_KEY_ALIAS],
        )
