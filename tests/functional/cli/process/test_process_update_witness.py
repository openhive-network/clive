from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.keys.keys import PrivateKey
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.schemas import (
    FeedPublishOperation,
    OperationBase,
    WitnessSetPropertiesOperation,
    WitnessUpdateOperation,
)
from clive_local_tools.checkers.blockchain_checkers import (
    assert_operation_type_in_blockchain,
)
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

import test_tools as tt

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)
MEMO: Final[str] = "test-process-transfer-memo"


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_account_creation_fee(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_active_authority: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if use_active_authority else [WitnessSetPropertiesOperation]
    )
    amount = tt.Asset.Hive(3.456)

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_active_authority=use_active_authority, account_creation_fee=amount
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert witness.props.account_creation_fee is not None, "Account creation fee should be set during witness creation"
    assert amount == witness.props.account_creation_fee, (
        f"Witness '{owner}' account creation fee should change after command witness-update,"
        f" expected: `{amount.pretty_amount()}`, actual: `{witness.props.account_creation_fee.pretty_amount()}`"
    )


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_maximum_block_size(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_active_authority: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if use_active_authority else [WitnessSetPropertiesOperation]
    )
    maximum_block_size = 1_048_576

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_active_authority=use_active_authority, maximum_block_size=maximum_block_size
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert maximum_block_size == witness.props.maximum_block_size, (
        f"Witness '{owner}' maximum block size should change after command witness-update,"
        f" expected: `{maximum_block_size}`, actual: `{witness.props.maximum_block_size}`"
    )


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_hbd_interest_rate(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_active_authority: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if use_active_authority else [WitnessSetPropertiesOperation]
    )
    hbd_interest_rate = Decimal("54.32")

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_active_authority=use_active_authority, hbd_interest_rate=hbd_interest_rate
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert percent_to_hive_percent(hbd_interest_rate) == witness.props.hbd_interest_rate, (
        f"Witness '{owner}' hbd interest rate should change after command witness-update,"
        f" expected: `{percent_to_hive_percent(hbd_interest_rate)}`, actual: `{witness.props.hbd_interest_rate}`"
    )


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_new_signing_key(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_active_authority: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if use_active_authority else [WitnessSetPropertiesOperation]
    )
    new_signing_key = PrivateKey.create().calculate_public_key().value

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_active_authority=use_active_authority, new_signing_key=new_signing_key
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert new_signing_key == witness.signing_key, (
        f"Witness '{owner}' signing key should change after command witness-update,"
        f" expected: `{new_signing_key}`, actual: `{witness.signing_key}`"
    )


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_hbd_exchange_rate(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_active_authority: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [FeedPublishOperation] if use_active_authority else [WitnessSetPropertiesOperation]
    )
    hbd_exchange_rate = 0.234

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_active_authority=use_active_authority, hbd_exchange_rate=hbd_exchange_rate
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    actual_exchange_rate = witness.hbd_exchange_rate.base / witness.hbd_exchange_rate.quote
    assert hbd_exchange_rate == actual_exchange_rate, (
        f"Witness '{owner}' hbd exchange rate should change after command witness-update,"
        f" expected: `{hbd_exchange_rate}`, actual: `{actual_exchange_rate}`"
    )


@pytest.mark.parametrize("use_active_authority", [True, False])
async def test_url(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_active_authority: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if use_active_authority else [WitnessSetPropertiesOperation]
    )
    url = "example.com"

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_active_authority=use_active_authority, url=url
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert url == witness.url, (
        f"Witness '{owner}' url change after command witness-update, expected: `{url}`, actual: `{witness.url}`"
    )


async def test_account_subsidy_budget(node: tt.RawNode, cli_tester_unlocked_with_witness_profile: CLITester) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = [WitnessSetPropertiesOperation]
    account_subsidy_budget = 1234

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        account_subsidy_budget=account_subsidy_budget
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert account_subsidy_budget == witness.props.account_subsidy_budget, (
        f"Witness '{owner}' account subsidy budget change after command witness-update,"
        f" expected: `{account_subsidy_budget}`, actual: `{witness.props.account_subsidy_budget}`"
    )


async def test_account_subsidy_decay(node: tt.RawNode, cli_tester_unlocked_with_witness_profile: CLITester) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = [WitnessSetPropertiesOperation]
    account_subsidy_decay = 5678

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        account_subsidy_decay=account_subsidy_decay
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert account_subsidy_decay == witness.props.account_subsidy_decay, (
        f"Witness '{owner}' account subsidy decay should change after command witness-update,"
        f" expected: `{account_subsidy_decay}`, actual: `{witness.props.account_subsidy_decay}`"
    )


async def test_two_operations_in_transaction(
    node: tt.RawNode, cli_tester_unlocked_with_witness_profile: CLITester
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = [WitnessUpdateOperation, FeedPublishOperation]
    hbd_exchange_rate = 0.3456
    hbd_interest_rate = Decimal("65.43")

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_active_authority=True, hbd_exchange_rate=hbd_exchange_rate, hbd_interest_rate=hbd_interest_rate
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    actual_exchange_rate = witness.hbd_exchange_rate.base / witness.hbd_exchange_rate.quote
    assert hbd_exchange_rate == actual_exchange_rate, (
        f"Witness '{owner}' hbd exchange rate should change after command witness-update,"
        f" expected: `{hbd_exchange_rate}`, actual: `{actual_exchange_rate}`"
    )
    assert percent_to_hive_percent(hbd_interest_rate) == witness.props.hbd_interest_rate, (
        f"Witness '{owner}' hbd interest rate should change after command witness-update,"
        f" expected: `{percent_to_hive_percent(hbd_interest_rate)}`, actual: `{witness.props.hbd_interest_rate}`"
    )


async def test_using_updated_witness_key(node: tt.RawNode, cli_tester_unlocked_with_witness_profile: CLITester) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = [WitnessSetPropertiesOperation]
    account_subsidy_decay = 6543
    alias = "updated_signing_key"
    new_private_signing_key = PrivateKey.create()
    cli_tester_unlocked_with_witness_profile.process_update_witness(
        new_signing_key=new_private_signing_key.calculate_public_key().value
    )
    cli_tester_unlocked_with_witness_profile.configure_key_add(key=new_private_signing_key.value, alias=alias)

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        account_subsidy_decay=account_subsidy_decay, sign_with=alias
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert account_subsidy_decay == witness.props.account_subsidy_decay, (
        f"Witness '{owner}' account subsidy decay should change after command witness-update,"
        f" expected: `{account_subsidy_decay}`, actual: `{witness.props.account_subsidy_decay}`"
    )
