from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.cli.commands.process.process_update_witness import CLIRequiresWitnessSetPropertiesOperationError
from clive.__private.core.formatters.case import dasherize
from clive.__private.core.keys.keys import PrivateKey, PublicKey
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import (
    FeedPublishOperation,
    OperationBase,
    WitnessSetPropertiesOperation,
    WitnessUpdateOperation,
)
from clive_local_tools.checkers.blockchain_checkers import assert_operation_type_in_blockchain, assert_witness_property
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.helpers import get_formatted_error_message

if TYPE_CHECKING:
    import test_tools as tt

    from clive_local_tools.cli.cli_tester import CLITester

NEW_SIGNING_KEY: Final[PublicKey] = PublicKey(
    value="STM6aacAN2UoV723iH3Ko1tJZVbNjtPeJoP7AxDu9XPczafp4UQWc"
)  # random key


@pytest.mark.parametrize(
    ("use_witness_key", "property_name", "property_value", "operation_type"),
    [
        (True, "account_creation_fee", Asset.hive("3.456"), WitnessSetPropertiesOperation),
        (False, "account_creation_fee", Asset.hive("3.456"), WitnessUpdateOperation),
        (True, "maximum_block_size", 1_048_576, WitnessSetPropertiesOperation),
        (False, "maximum_block_size", 1_048_576, WitnessUpdateOperation),
        (True, "hbd_interest_rate", Decimal("54.32"), WitnessSetPropertiesOperation),
        (False, "hbd_interest_rate", Decimal("54.32"), WitnessUpdateOperation),
        (True, "new_signing_key", NEW_SIGNING_KEY.value, WitnessSetPropertiesOperation),
        (False, "new_signing_key", NEW_SIGNING_KEY.value, WitnessUpdateOperation),
        (True, "hbd_exchange_rate", Asset.hbd("0.234"), WitnessSetPropertiesOperation),
        (False, "hbd_exchange_rate", Asset.hbd("0.234"), FeedPublishOperation),
        (True, "url", "example.com", WitnessSetPropertiesOperation),
        (False, "url", "example.com", WitnessUpdateOperation),
        (True, "account_subsidy_budget", 1234, WitnessSetPropertiesOperation),
        (True, "account_subsidy_decay", 5678, WitnessSetPropertiesOperation),
    ],
)
async def test_setting_witness_property(  # noqa: PLR0913
    node: tt.RawNode,
    cli_tester_unlocked_with_witness_profile: CLITester,
    use_witness_key: bool,  # noqa: FBT001
    property_name: str,
    property_value: str | int | Decimal | Asset.LiquidT,
    operation_type: type[OperationBase],
) -> None:
    # ARRANGE
    cli_tester = cli_tester_unlocked_with_witness_profile
    owner = cli_tester.world.profile.accounts.working.name
    properties = {property_name: property_value}

    # ACT
    result = cli_tester.process_update_witness(use_witness_key=use_witness_key, **properties)  # type: ignore[arg-type]

    # ASSERT
    assert_operation_type_in_blockchain(node, result, operation_type)
    witness = (await cli_tester.world.commands.find_witness(witness_name=owner)).result_or_raise
    assert_witness_property(property_name, property_value, witness)


async def test_two_operations_in_transaction(
    node: tt.RawNode, cli_tester_unlocked_with_witness_profile: CLITester
) -> None:
    # ARRANGE
    operations: list[type[OperationBase]] = [WitnessUpdateOperation, FeedPublishOperation]
    hbd_exchange_rate = Asset.hbd("0.3456")
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
    assert witness.hbd_exchange_rate.quote == Asset.hive(1), "hbd exchange rate should be given as price of 1 hive"
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


@pytest.mark.parametrize(
    ("property_name", "property_value"),
    [
        ("account_subsidy_budget", 1234),
        ("account_subsidy_decay", 5678),
    ],
)
async def test_negative_account_subsidy_with_active_authority(
    cli_tester_unlocked_with_witness_profile: CLITester, property_name: str, property_value: int
) -> None:
    """Test exception is thrown when attempting to modify account-subsidy properties and sign it with active key."""
    # ARRANGE
    cli_tester = cli_tester_unlocked_with_witness_profile
    properties = {property_name: property_value}

    # ACT & ASSERT
    with pytest.raises(
        CLITestCommandError,
        match=get_formatted_error_message(CLIRequiresWitnessSetPropertiesOperationError(dasherize(property_name))),
    ):
        cli_tester.process_update_witness(use_witness_key=False, **properties)  # type: ignore[arg-type]
