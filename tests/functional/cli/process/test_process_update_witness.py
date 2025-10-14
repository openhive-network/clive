from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
import test_tools as tt

from clive.__private.cli.commands.process.process_update_witness import RequiresWitnessSetPropertiesOperationError
from clive.__private.core.keys.keys import PrivateKey
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.schemas import (
    FeedPublishOperation,
    OperationBase,
    WitnessSetPropertiesOperation,
    WitnessUpdateOperation,
)
from clive_local_tools.checkers.blockchain_checkers import assert_operation_type_in_blockchain
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import get_formatted_error_message

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.mark.parametrize("use_witness_key", [True, False])
async def test_account_creation_fee(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_witness_key: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if not use_witness_key else [WitnessSetPropertiesOperation]
    )
    amount = tt.Asset.Hive(3.456)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_witness_key=use_witness_key, account_creation_fee=amount
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert witness.props.account_creation_fee is not None, "Account creation fee should be set during witness creation"
    assert amount == witness.props.account_creation_fee, (
        f"Witness '{owner}' account creation fee should change after command witness-update,"
        f" expected: `{amount.pretty_amount()}`, actual: `{witness.props.account_creation_fee.pretty_amount()}`"
    )


@pytest.mark.parametrize("use_witness_key", [True, False])
async def test_maximum_block_size(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_witness_key: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if not use_witness_key else [WitnessSetPropertiesOperation]
    )
    maximum_block_size = 1_048_576
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_witness_key=use_witness_key, maximum_block_size=maximum_block_size
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert maximum_block_size == witness.props.maximum_block_size, (
        f"Witness '{owner}' maximum block size should change after command witness-update,"
        f" expected: `{maximum_block_size}`, actual: `{witness.props.maximum_block_size}`"
    )


@pytest.mark.parametrize("use_witness_key", [True, False])
async def test_hbd_interest_rate(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_witness_key: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if not use_witness_key else [WitnessSetPropertiesOperation]
    )
    hbd_interest_rate = Decimal("54.32")
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_witness_key=use_witness_key, hbd_interest_rate=hbd_interest_rate
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert percent_to_hive_percent(hbd_interest_rate) == witness.props.hbd_interest_rate, (
        f"Witness '{owner}' hbd interest rate should change after command witness-update,"
        f" expected: `{percent_to_hive_percent(hbd_interest_rate)}`, actual: `{witness.props.hbd_interest_rate}`"
    )


@pytest.mark.parametrize("use_witness_key", [True, False])
async def test_new_signing_key(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_witness_key: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if not use_witness_key else [WitnessSetPropertiesOperation]
    )
    new_signing_key = PrivateKey.create().calculate_public_key().value
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_witness_key=use_witness_key, new_signing_key=new_signing_key
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert new_signing_key == witness.signing_key, (
        f"Witness '{owner}' signing key should change after command witness-update,"
        f" expected: `{new_signing_key}`, actual: `{witness.signing_key}`"
    )


@pytest.mark.parametrize("use_witness_key", [True, False])
async def test_hbd_exchange_rate(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_witness_key: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [FeedPublishOperation] if not use_witness_key else [WitnessSetPropertiesOperation]
    )
    hbd_exchange_rate = tt.Asset.Hbd(0.234)
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_witness_key=use_witness_key, hbd_exchange_rate=hbd_exchange_rate
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert witness.hbd_exchange_rate.base == hbd_exchange_rate, (
        f"Witness '{owner}' hbd exchange rate should change after command witness-update,"
        f" expected: `{hbd_exchange_rate}`, actual: `{witness.hbd_exchange_rate.base}`"
    )
    assert witness.hbd_exchange_rate.quote == tt.Asset.Hive(1), "hbd exchange rate should be given as price of 1 hive"


@pytest.mark.parametrize("use_witness_key", [True, False])
async def test_url(
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_witness_key: bool,  # noqa: FBT001
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = (
        [WitnessUpdateOperation] if not use_witness_key else [WitnessSetPropertiesOperation]
    )
    url = "example.com"
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(use_witness_key=use_witness_key, url=url)

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
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
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        account_subsidy_budget=account_subsidy_budget
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
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
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        account_subsidy_decay=account_subsidy_decay
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
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
    hbd_exchange_rate = tt.Asset.Hbd(0.3456)
    hbd_interest_rate = Decimal("65.43")
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        use_witness_key=False, hbd_exchange_rate=hbd_exchange_rate, hbd_interest_rate=hbd_interest_rate
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert witness.hbd_exchange_rate.base == hbd_exchange_rate, (
        f"Witness '{owner}' hbd exchange rate should change after command witness-update,"
        f" expected: `{hbd_exchange_rate}`, actual: `{witness.hbd_exchange_rate.base}`"
    )
    assert witness.hbd_exchange_rate.quote == tt.Asset.Hive(1), "hbd exchange rate should be given as price of 1 hive"
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
    owner = cli_tester_unlocked_with_witness_profile.world.profile.accounts.working.name

    # ACT
    result = cli_tester_unlocked_with_witness_profile.process_update_witness(
        account_subsidy_decay=account_subsidy_decay, sign_with=alias
    )

    # ASSERT
    assert_operation_type_in_blockchain(node, result, *operations)
    witness = (
        await cli_tester_unlocked_with_witness_profile.world.commands.find_witness(witness_name=owner)
    ).result_or_raise
    assert account_subsidy_decay == witness.props.account_subsidy_decay, (
        f"Witness '{owner}' account subsidy decay should change after command witness-update,"
        f" expected: `{account_subsidy_decay}`, actual: `{witness.props.account_subsidy_decay}`"
    )


async def test_negative_account_subsidy_with_active_authority(
    cli_tester_unlocked_with_witness_profile: CLITester,
) -> None:
    # ARRANGE
    account_subsidy_budget = 2345

    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError,
        match=get_formatted_error_message(RequiresWitnessSetPropertiesOperationError("account-subsidy-budget")),
    ):
        cli_tester_unlocked_with_witness_profile.process_update_witness(
            use_witness_key=False, account_subsidy_budget=account_subsidy_budget
        )
