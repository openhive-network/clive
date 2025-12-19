from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from clive.__private.cli.exceptions import ProcessTransferScheduleNullPairIdError
from clive.__private.models.asset import Asset


def _default_amount() -> Asset.LiquidT:
    return Asset.hive(1)


def _default_datetime() -> datetime:
    return datetime.now(tz=UTC)


def _default_hive() -> Asset.Hive:
    return Asset.hive(100)


def _default_hbd() -> Asset.Hbd:
    return Asset.hbd(100)


@dataclass
class MockScheduledTransfer:
    """Mock ScheduledTransfer for testing."""

    to: str
    pair_id: int
    amount: Asset.LiquidT = field(default_factory=_default_amount)
    consecutive_failures: int = 0
    from_: str = "alice"
    memo: str = ""
    recurrence: int = 24
    remaining_executions: int = 2
    trigger_date: datetime = field(default_factory=_default_datetime)


@dataclass
class MockAccountScheduledTransferData:
    """Mock AccountScheduledTransferData for testing."""

    scheduled_transfers: list[MockScheduledTransfer]
    account_hive_balance: Asset.Hive = field(default_factory=_default_hive)
    account_hbd_balance: Asset.Hbd = field(default_factory=_default_hbd)

    def filter_by_receiver(self, receiver: str) -> list[MockScheduledTransfer]:
        return [st for st in self.scheduled_transfers if st.to == receiver]

    def has_any_scheduled_transfers(self) -> bool:
        return bool(self.scheduled_transfers)


class ValidationLogicTester:
    """Helper class to test validation logic from _ProcessTransferScheduleCommon."""

    def __init__(
        self,
        to: str,
        pair_id: int | None,
        account_scheduled_transfers_data: MockAccountScheduledTransferData,
    ) -> None:
        self.to = to
        self.pair_id = pair_id
        self.account_scheduled_transfers_data = account_scheduled_transfers_data

    def validate_pair_id_should_be_given(self) -> None:
        """
        Validate if pair_id should be specified explicitly.

        Rules:
        - If pair_id is specified, OK
        - If there's exactly one transfer to receiver with pair_id=0, auto-select OK
        - Otherwise (multiple transfers OR single transfer with pair_id != 0), error
        """
        if self.pair_id is not None:
            return

        transfers_to_receiver = self.account_scheduled_transfers_data.filter_by_receiver(self.to)

        if len(transfers_to_receiver) == 0:
            return  # No transfers, will fail on existence check

        if len(transfers_to_receiver) == 1:
            if transfers_to_receiver[0].pair_id == 0:
                return  # Single transfer with pair_id=0, auto-select OK
            # Single transfer with pair_id != 0
            raise ProcessTransferScheduleNullPairIdError(self.to, existing_pair_id=transfers_to_receiver[0].pair_id)

        # Multiple transfers
        raise ProcessTransferScheduleNullPairIdError(self.to)

    def identity_check(self, scheduled_transfer: MockScheduledTransfer) -> bool:
        """Determine if a scheduled transfer matches destination and the specified pair ID."""
        if scheduled_transfer.to != self.to:
            return False

        if self.pair_id is not None:
            return scheduled_transfer.pair_id == self.pair_id

        # pair_id not specified - check if we can auto-select
        transfers_to_receiver = self.account_scheduled_transfers_data.filter_by_receiver(self.to)
        if len(transfers_to_receiver) == 1 and transfers_to_receiver[0].pair_id == 0:
            # Single transfer with pair_id=0, auto-select it
            return scheduled_transfer.pair_id == 0

        # Default behavior: treat None as 0
        return scheduled_transfer.pair_id == 0


# Tests for validate_pair_id_should_be_given


def test_validate_pair_id_given_explicitly_passes() -> None:
    # Arrange
    transfers = [MockScheduledTransfer(to="bob", pair_id=5)]
    data = MockAccountScheduledTransferData(scheduled_transfers=transfers)
    tester = ValidationLogicTester(to="bob", pair_id=5, account_scheduled_transfers_data=data)

    # Act & Assert - should not raise
    tester.validate_pair_id_should_be_given()


def test_validate_single_transfer_with_pair_id_0_auto_selects() -> None:
    # Arrange
    transfers = [MockScheduledTransfer(to="bob", pair_id=0)]
    data = MockAccountScheduledTransferData(scheduled_transfers=transfers)
    tester = ValidationLogicTester(to="bob", pair_id=None, account_scheduled_transfers_data=data)

    # Act & Assert - should not raise (auto-select)
    tester.validate_pair_id_should_be_given()


def test_validate_single_transfer_with_nonzero_pair_id_requires_explicit() -> None:
    # Arrange
    transfers = [MockScheduledTransfer(to="bob", pair_id=5)]
    data = MockAccountScheduledTransferData(scheduled_transfers=transfers)
    tester = ValidationLogicTester(to="bob", pair_id=None, account_scheduled_transfers_data=data)

    # Act & Assert
    with pytest.raises(ProcessTransferScheduleNullPairIdError) as exc_info:
        tester.validate_pair_id_should_be_given()
    assert "bob" in str(exc_info.value)
    assert "pair_id=`5`" in str(exc_info.value)  # Should show existing pair_id


def test_validate_multiple_transfers_requires_explicit_pair_id() -> None:
    # Arrange
    transfers = [
        MockScheduledTransfer(to="bob", pair_id=0),
        MockScheduledTransfer(to="bob", pair_id=1),
    ]
    data = MockAccountScheduledTransferData(scheduled_transfers=transfers)
    tester = ValidationLogicTester(to="bob", pair_id=None, account_scheduled_transfers_data=data)

    # Act & Assert
    with pytest.raises(ProcessTransferScheduleNullPairIdError) as exc_info:
        tester.validate_pair_id_should_be_given()
    assert "bob" in str(exc_info.value)
    assert "Cannot determine" in str(exc_info.value)  # Multiple transfers message


def test_validate_no_transfers_passes() -> None:
    # Arrange
    data = MockAccountScheduledTransferData(scheduled_transfers=[])
    tester = ValidationLogicTester(to="bob", pair_id=None, account_scheduled_transfers_data=data)

    # Act & Assert - should not raise (existence check handles this)
    tester.validate_pair_id_should_be_given()


# Tests for identity_check


def test_identity_check_with_explicit_pair_id_matches() -> None:
    # Arrange
    transfer = MockScheduledTransfer(to="bob", pair_id=5)
    data = MockAccountScheduledTransferData(scheduled_transfers=[transfer])
    tester = ValidationLogicTester(to="bob", pair_id=5, account_scheduled_transfers_data=data)

    # Act
    result = tester.identity_check(transfer)

    # Assert
    assert result is True


def test_identity_check_with_explicit_pair_id_no_match() -> None:
    # Arrange
    transfer = MockScheduledTransfer(to="bob", pair_id=5)
    data = MockAccountScheduledTransferData(scheduled_transfers=[transfer])
    tester = ValidationLogicTester(to="bob", pair_id=3, account_scheduled_transfers_data=data)

    # Act
    result = tester.identity_check(transfer)

    # Assert
    assert result is False


def test_identity_check_auto_selects_single_transfer_with_pair_id_0() -> None:
    # Arrange
    transfer = MockScheduledTransfer(to="bob", pair_id=0)
    data = MockAccountScheduledTransferData(scheduled_transfers=[transfer])
    tester = ValidationLogicTester(to="bob", pair_id=None, account_scheduled_transfers_data=data)

    # Act
    result = tester.identity_check(transfer)

    # Assert
    assert result is True


def test_identity_check_wrong_receiver_returns_false() -> None:
    # Arrange
    transfer = MockScheduledTransfer(to="charlie", pair_id=0)
    data = MockAccountScheduledTransferData(scheduled_transfers=[transfer])
    tester = ValidationLogicTester(to="bob", pair_id=None, account_scheduled_transfers_data=data)

    # Act
    result = tester.identity_check(transfer)

    # Assert
    assert result is False


def test_identity_check_multiple_transfers_defaults_to_pair_id_0() -> None:
    # Arrange
    transfer_0 = MockScheduledTransfer(to="bob", pair_id=0)
    transfer_1 = MockScheduledTransfer(to="bob", pair_id=1)
    data = MockAccountScheduledTransferData(scheduled_transfers=[transfer_0, transfer_1])
    tester = ValidationLogicTester(to="bob", pair_id=None, account_scheduled_transfers_data=data)

    # Act
    result_0 = tester.identity_check(transfer_0)
    result_1 = tester.identity_check(transfer_1)

    # Assert
    assert result_0 is True  # pair_id=0 matches default
    assert result_1 is False  # pair_id=1 does not match default
