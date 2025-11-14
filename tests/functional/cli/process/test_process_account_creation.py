from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.core.constants.cli import DEFAULT_AUTHORITY_THRESHOLD, DEFAULT_AUTHORITY_WEIGHT
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.models.schemas import (
    AccountCreateOperation,
    AssetHive,
    Authority,
    CreateClaimedAccountOperation,
    PublicKey,
)
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operations_placed_in_blockchain,
    assert_transaction_in_blockchain,
)
from clive_local_tools.helpers import create_transaction_filepath
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    import test_tools as tt

    from clive.__private.core.types import AuthorityLevel
    from clive_local_tools.cli.cli_tester import CLITester


NEW_ACCOUNT_NAME: Final[str] = "newaccount"
OTHER_ACCOUNT2: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[1].account
WEIGHT: Final[int] = 213
MODIFIED_WEIGHT: Final[int] = 214
WEIGHT_THRESHOLD: Final[int] = 2


def create_public_key_for_role(new_account_name: str = NEW_ACCOUNT_NAME, *, role: AuthorityLevel) -> PublicKey:
    private_key = PrivateKey.generate_from_seed("seed", new_account_name, role=role)
    return private_key.calculate_public_key().value


OWNER_KEY: Final[PublicKey] = create_public_key_for_role(role="owner")
OWNER_AUTHORITY: Final[Authority] = Authority(
    weight_threshold=DEFAULT_AUTHORITY_THRESHOLD,
    account_auths=[],
    key_auths=[(OWNER_KEY, DEFAULT_AUTHORITY_WEIGHT)],
)
ACTIVE_KEY: Final[PublicKey] = create_public_key_for_role(role="active")
ACTIVE_AUTHORITY: Final[Authority] = Authority(
    weight_threshold=DEFAULT_AUTHORITY_THRESHOLD,
    account_auths=[],
    key_auths=[(ACTIVE_KEY, DEFAULT_AUTHORITY_WEIGHT)],
)
POSTING_KEY: Final[PublicKey] = create_public_key_for_role(role="posting")
POSTING_AUTHORITY: Final[Authority] = Authority(
    weight_threshold=DEFAULT_AUTHORITY_THRESHOLD,
    account_auths=[],
    key_auths=[(POSTING_KEY, DEFAULT_AUTHORITY_WEIGHT)],
)
MEMO_KEY: Final[PublicKey] = create_public_key_for_role(role="memo")


def fetch_account_creation_fee(node: tt.RawNode) -> AssetHive:
    fee = node.api.database_api.get_witness_schedule().median_props.account_creation_fee
    assert fee is not None, "Account creation fee should be present in database_api.get_witness_schedule"
    return fee


async def test_account_creation_with_fee(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    fee = fetch_account_creation_fee(node)
    operation = AccountCreateOperation(
        fee=fee,
        creator=WORKING_ACCOUNT_DATA.account.name,
        new_account_name=NEW_ACCOUNT_NAME,
        owner=OWNER_AUTHORITY,
        active=ACTIVE_AUTHORITY,
        posting=POSTING_AUTHORITY,
        memo_key=MEMO_KEY,
        json_metadata="",
    )

    # ACT
    result = cli_tester.process_account_creation(
        new_account_name=operation.new_account_name,
        owner=OWNER_KEY,
        active=ACTIVE_KEY,
        posting=POSTING_KEY,
        memo=operation.memo_key,
        fee=True,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_account_creation_with_token(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    # in block_log only initminer has account subsidies so we pay fee to get token
    fee = fetch_account_creation_fee(node)
    cli_tester.process_claim_new_account_token(fee=fee)
    operation = CreateClaimedAccountOperation(
        creator=WORKING_ACCOUNT_DATA.account.name,
        new_account_name=NEW_ACCOUNT_NAME,
        owner=OWNER_AUTHORITY,
        active=ACTIVE_AUTHORITY,
        posting=POSTING_AUTHORITY,
        memo_key=MEMO_KEY,
        json_metadata="",
    )

    # ACT
    result = cli_tester.process_account_creation(
        new_account_name=operation.new_account_name,
        owner=OWNER_KEY,
        active=ACTIVE_KEY,
        posting=POSTING_KEY,
        memo=operation.memo_key,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_save_to_file(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    transaction_filepath = create_transaction_filepath()

    # ACT
    cli_tester.process_account_creation(
        new_account_name=NEW_ACCOUNT_NAME,
        owner=OWNER_KEY,
        active=ACTIVE_KEY,
        posting=POSTING_KEY,
        memo=MEMO_KEY,
        fee=True,
        broadcast=False,
        save_file=transaction_filepath,
    )

    # ASSERT
    result = cli_tester.process_transaction(from_file=transaction_filepath)
    assert_transaction_in_blockchain(node, result)


async def test_positional_arguments_are_allowed(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    fee = fetch_account_creation_fee(node)
    operation = AccountCreateOperation(
        fee=fee,
        creator=WORKING_ACCOUNT_DATA.account.name,
        new_account_name=NEW_ACCOUNT_NAME,
        owner=OWNER_AUTHORITY,
        active=ACTIVE_AUTHORITY,
        posting=POSTING_AUTHORITY,
        memo_key=MEMO_KEY,
        json_metadata="",
    )

    # ACT
    result = cli_tester.process_account_creation(
        operation.new_account_name,
        OWNER_KEY,
        ACTIVE_KEY,
        POSTING_KEY,
        operation.memo_key,
        fee=True,
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
