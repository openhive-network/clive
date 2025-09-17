from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.commands.process.process_account_creation import (
    MissingActiveAuthorityError,
    MissingMemoKeyError,
    MissingOwnerAuthorityError,
    MissingPostingAuthorityError,
)
from clive.__private.core import iwax
from clive.__private.core.constants.cli import NEW_ACCOUNT_AUTHORITY_THRESOHLD, NEW_ACCOUNT_AUTHORITY_WEIGHT
from clive.__private.core.keys import PrivateKey
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
    assert_transaction_not_in_blockchain,
)
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester


NEW_ACCOUNT_NAME: Final[str] = "newaccount"
OTHER_ACCOUNT2: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[1].account
WEIGHT: Final[int] = 213
MODIFIED_WEIGHT: Final[int] = 214
WEIGHT_THRESHOLD: Final[int] = 2


def create_public_key_for_role(role: str) -> PublicKey:
    private_key = iwax.generate_password_based_private_key("password", role, NEW_ACCOUNT_NAME)
    return private_key.calculate_public_key().value


OWNER_KEY: Final[PublicKey] = create_public_key_for_role("owner")
OWNER_AUTHORITY: Final[Authority] = Authority(
    weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD,
    account_auths=[],
    key_auths=[(OWNER_KEY, NEW_ACCOUNT_AUTHORITY_WEIGHT)],
)
ACTIVE_KEY: Final[PublicKey] = create_public_key_for_role("active")
ACTIVE_AUTHORITY: Final[Authority] = Authority(
    weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD,
    account_auths=[],
    key_auths=[(ACTIVE_KEY, NEW_ACCOUNT_AUTHORITY_WEIGHT)],
)
POSTING_KEY: Final[PublicKey] = create_public_key_for_role("posting")
POSTING_AUTHORITY: Final[Authority] = Authority(
    weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD,
    account_auths=[],
    key_auths=[(POSTING_KEY, NEW_ACCOUNT_AUTHORITY_WEIGHT)],
)
MEMO_KEY: Final[PublicKey] = create_public_key_for_role("memo")


def format_auths_arg(authority_entries: list[tuple[PublicKey | str, int]]) -> list[str]:
    return [f"{entry[0]}={entry[1]}" for entry in authority_entries]


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
    result = (
        cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True)
        .owner(key=OWNER_KEY)
        .active(key=ACTIVE_KEY)
        .posting(key=POSTING_KEY)
        .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
        .fire()
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_account_creation_with_token(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    # in block_log only initminer has account subsidies so we pay fee to get token
    fee = fetch_account_creation_fee(node)
    cli_tester.process_claim_new_account_token(sign_with=WORKING_ACCOUNT_KEY_ALIAS, fee=fee)
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
    result = (
        cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME)
        .owner(key=OWNER_KEY)
        .active(key=ACTIVE_KEY)
        .posting(key=POSTING_KEY)
        .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
        .fire()
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_account_creation_authority_with_weight(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    fee = fetch_account_creation_fee(node)
    weight = 5
    posting_authority_with_weight: Final[Authority] = Authority(
        weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD,
        account_auths=[],
        key_auths=[(POSTING_KEY, weight)],
    )
    operation = AccountCreateOperation(
        fee=fee,
        creator=WORKING_ACCOUNT_DATA.account.name,
        new_account_name=NEW_ACCOUNT_NAME,
        owner=OWNER_AUTHORITY,
        active=ACTIVE_AUTHORITY,
        posting=posting_authority_with_weight,
        memo_key=MEMO_KEY,
        json_metadata="",
    )

    # ACT
    result = (
        cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True)
        .owner(key=OWNER_KEY)
        .active(key=ACTIVE_KEY)
        .posting(key=format_auths_arg(posting_authority_with_weight.key_auths))
        .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
        .fire()
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_account_creation_multiple_subcommands(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    fee = fetch_account_creation_fee(node)
    additional_posting_key: PublicKey = PrivateKey.create().calculate_public_key().value
    posting_authority_multiple_keys: Final[Authority] = Authority(
        weight_threshold=NEW_ACCOUNT_AUTHORITY_THRESOHLD,
        account_auths=[
            (WATCHED_ACCOUNTS_DATA[0].account.name, NEW_ACCOUNT_AUTHORITY_WEIGHT),
        ],
        key_auths=[(POSTING_KEY, NEW_ACCOUNT_AUTHORITY_WEIGHT), (additional_posting_key, NEW_ACCOUNT_AUTHORITY_WEIGHT)],
    )
    operation = AccountCreateOperation(
        fee=fee,
        creator=WORKING_ACCOUNT_DATA.account.name,
        new_account_name=NEW_ACCOUNT_NAME,
        owner=OWNER_AUTHORITY,
        active=ACTIVE_AUTHORITY,
        posting=posting_authority_multiple_keys,
        memo_key=MEMO_KEY,
        json_metadata="",
    )

    # ACT
    result = (
        cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True)
        .owner(key=OWNER_KEY)
        .active(key=ACTIVE_KEY)
        .posting(key=POSTING_KEY)
        .posting(key=additional_posting_key)
        .posting(account=WATCHED_ACCOUNTS_DATA[0].account.name)
        .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
        .fire()
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_account_creation_complex_authority(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ARRANGE
    fee = fetch_account_creation_fee(node)
    threshold = 2
    weight = 2
    other_key = create_public_key_for_role("other")
    complex_owner_authority = Authority(
        weight_threshold=threshold,
        account_auths=[
            (WATCHED_ACCOUNTS_DATA[0].account.name, weight),
            (WATCHED_ACCOUNTS_DATA[1].account.name, weight),
        ],
        key_auths=[(OWNER_KEY, weight), (other_key, weight)],
    )
    complex_active_authority = Authority(
        weight_threshold=threshold,
        account_auths=[
            (WATCHED_ACCOUNTS_DATA[0].account.name, weight),
            (WATCHED_ACCOUNTS_DATA[2].account.name, weight),
        ],
        key_auths=[(ACTIVE_KEY, weight), (other_key, weight)],
    )
    complex_posting_authority = Authority(
        weight_threshold=threshold,
        account_auths=[(WATCHED_ACCOUNTS_DATA[0].account.name, weight)],
        key_auths=[(POSTING_KEY, weight), (other_key, weight)],
    )
    operation = AccountCreateOperation(
        fee=fee,
        creator=WORKING_ACCOUNT_DATA.account.name,
        new_account_name=NEW_ACCOUNT_NAME,
        owner=complex_owner_authority,
        active=complex_active_authority,
        posting=complex_posting_authority,
        memo_key=MEMO_KEY,
        json_metadata="",
    )

    # ACT
    result = (
        cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True)
        .owner(
            account=format_auths_arg(complex_owner_authority.account_auths),
            key=format_auths_arg(complex_owner_authority.key_auths),
            threshold=threshold,
        )
        .active(
            account=format_auths_arg(complex_active_authority.account_auths),
            key=format_auths_arg(complex_active_authority.key_auths),
            threshold=threshold,
        )
        .posting(
            account=format_auths_arg(complex_posting_authority.account_auths),
            key=format_auths_arg(complex_posting_authority.key_auths),
            threshold=threshold,
        )
        .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
        .fire()
    )

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)


async def test_negative_empty_owner_authority(cli_tester: CLITester) -> None:
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=MissingOwnerAuthorityError.MESSAGE):
        (
            cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True)
            .active(key=ACTIVE_KEY)
            .posting(key=POSTING_KEY)
            .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
            .fire()
        )


async def test_negative_empty_active_authority(cli_tester: CLITester) -> None:
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=MissingActiveAuthorityError.MESSAGE):
        (
            cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True)
            .owner(key=OWNER_KEY)
            .posting(key=POSTING_KEY)
            .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
            .fire()
        )


async def test_negative_empty_posting_authority(cli_tester: CLITester) -> None:
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=MissingPostingAuthorityError.MESSAGE):
        (
            cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True)
            .owner(key=OWNER_KEY)
            .active(key=ACTIVE_KEY)
            .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
            .fire()
        )


async def test_negative_no_memo_key(cli_tester: CLITester) -> None:
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=MissingMemoKeyError.MESSAGE):
        (
            cli_tester.process_account_creation(
                new_account_name=NEW_ACCOUNT_NAME, fee=True, sign_with=WORKING_ACCOUNT_KEY_ALIAS
            )
            .owner(key=OWNER_KEY)
            .active(key=ACTIVE_KEY)
            .posting(key=POSTING_KEY)
            .fire()
        )


async def test_dry_run(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    act_result = (
        cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True, broadcast=False)
        .owner(key=OWNER_KEY)
        .active(key=ACTIVE_KEY)
        .posting(key=POSTING_KEY)
        .memo(key=MEMO_KEY, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
        .fire()
    )

    # ASSERT
    assert_transaction_not_in_blockchain(node, act_result)


async def test_save_to_file(node: tt.RawNode, cli_tester: CLITester, tmp_path: Path) -> None:
    # ARRANGE
    trx_path = tmp_path / "account_creation.json"

    # ACT
    (
        cli_tester.process_account_creation(new_account_name=NEW_ACCOUNT_NAME, fee=True, broadcast=False)
        .owner(key=OWNER_KEY)
        .active(key=ACTIVE_KEY)
        .posting(key=POSTING_KEY)
        .memo(key=MEMO_KEY, save_file=trx_path, sign_with=WORKING_ACCOUNT_KEY_ALIAS)
        .fire()
    )

    # ASSERT
    result = cli_tester.process_transaction(from_file=trx_path)

    # ASSERT
    assert_transaction_in_blockchain(node, result)


async def test_account_creation_simple_workflow(node: tt.RawNode, cli_tester: CLITester) -> None:
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
        new_account_name=NEW_ACCOUNT_NAME,
        fee=True,
        specify_public_keys=(OWNER_KEY, ACTIVE_KEY, POSTING_KEY, MEMO_KEY),
        sign_with=WORKING_ACCOUNT_KEY_ALIAS,
    ).fire()

    # ASSERT
    assert_operations_placed_in_blockchain(node, result, operation)
