from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, override

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand
from clive.__private.cli.exceptions import CLIPrettyError, CLIWitnessNotFoundError
from clive.__private.core import iwax
from clive.__private.core.commands.find_witness import WitnessNotFoundError
from clive.__private.core.keys.keys import PublicKey
from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.asset import Asset
from clive.__private.models.schemas import (
    AccountName,
    FeedPublishOperation,
    HbdExchangeRate,
    LegacyChainProperties,
    WitnessSetPropertiesOperation,
    WitnessUpdateOperation,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.models.schemas import OperationBase


class RequiresWitnessSetPropertiesOperationError(CLIPrettyError):
    """
    Raised when operation must be signed with active authority but signing with witness key is requested.

    Args:
        property_name: Name of property that changing requires signing with witness key
            and operation witness_set_properties_operation.
    """

    def __init__(self, property_name: str) -> None:
        super().__init__(
            f"Changing property `{property_name}` can be performed in 'witness_set_properties_operation'"
            " and requires signing with witness signing key.\n"
            "You can skip option skip '--use-active-authority' or explicitly use '--no-use-active-authority'."
        )


@dataclass(kw_only=True)
class ProcessUpdateWitness(PerformActionsOnTransactionCommand):
    owner: str
    use_active_authority: bool
    account_creation_fee: Asset.Hive | None
    maximum_block_size: int | None
    hbd_interest_rate: Decimal | None
    account_subsidy_budget: int | None
    account_subsidy_decay: int | None
    new_signing_key: PublicKey | None
    hbd_exchange_rate: float | None
    url: str | None

    force_unsign: bool = field(init=False, default=False)

    @property
    def schemas_hbd_exchange_rate(self) -> HbdExchangeRate | None:
        return (
            HbdExchangeRate(base=Asset.Hbd(int(self.hbd_exchange_rate * 1000)), quote=Asset.Hive(1000))
            if self.hbd_exchange_rate
            else None
        )

    @override
    async def fetch_data(self) -> None:
        try:
            self.witness = (await self.world.commands.find_witness(witness_name=self.owner)).result_or_raise
        except WitnessNotFoundError as err:
            raise CLIWitnessNotFoundError(self.owner) from err

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        operations: list[OperationBase] = []
        if self._needs_feed_publish_operation:
            operations.append(self._create_feed_publish_operation())
        if self._needs_witness_update_operation:
            operations.append(self._create_witness_update_operation())
        if self._needs_witness_set_properties_operation:
            operations.append(self._create_witness_set_properties_operation())
        if not bool(operations):
            raise CLIPrettyError("no operations")
        return operations

    @override
    async def validate(self) -> None:
        self._validate_requirements_for_witness_set_propertues_operation()
        self._validate_if_broadcasting_signed_transaction()
        await super().validate()

    def _validate_requirements_for_witness_set_propertues_operation(self) -> None:
        if self.use_active_authority and self.account_subsidy_budget is not None:
            raise RequiresWitnessSetPropertiesOperationError("account-subsidy-budget")
        if self.use_active_authority and self.account_subsidy_decay is not None:
            raise RequiresWitnessSetPropertiesOperationError("account-subsidy-decay")

    @property
    def _needs_feed_publish_operation(self) -> bool:
        return self.use_active_authority and self.hbd_exchange_rate is not None

    @property
    def _needs_witness_set_properties_operation(self) -> bool:
        are_witness_set_properties_options_required: bool = (
            self.account_creation_fee is not None
            or self.maximum_block_size is not None
            or self.hbd_interest_rate is not None
            or self.new_signing_key is not None
            or self.url is not None
            or self.hbd_exchange_rate is not None
            or self.account_subsidy_budget is not None
            or self.account_subsidy_decay is not None
        )
        return not self.use_active_authority and are_witness_set_properties_options_required

    @property
    def _needs_witness_update_operation(self) -> bool:
        are_witness_update_options_required: bool = (
            self.account_creation_fee is not None
            or self.maximum_block_size is not None
            or self.hbd_interest_rate is not None
            or self.new_signing_key is not None
            or self.url is not None
        )
        return self.use_active_authority and are_witness_update_options_required

    def _create_feed_publish_operation(self) -> FeedPublishOperation:
        exchange_rate = self.schemas_hbd_exchange_rate
        assert exchange_rate is not None, (
            "Feed publish should be created only if command requires changing hbd_exchange_rate"
        )
        return FeedPublishOperation(
            publisher=AccountName(self.owner),
            exchange_rate=exchange_rate,
        )

    def _create_witness_update_operation(self) -> WitnessUpdateOperation:
        assert self.witness.props.account_creation_fee is not None, (
            "Account creation fee must be set during witness creation"
        )
        assert self.witness.props.maximum_block_size is not None, (
            "Maximum block size must be set during witness creation"
        )
        assert self.witness.props.hbd_interest_rate is not None, "Hbd interest rate must be set during witness creation"
        hbd_interest_rate = (
            percent_to_hive_percent(self.hbd_interest_rate)
            if self.hbd_interest_rate
            else self.witness.props.hbd_interest_rate
        )
        return WitnessUpdateOperation(
            owner=AccountName(self.owner),
            url=self.url or self.witness.url,
            block_signing_key=self.new_signing_key.value if self.new_signing_key else self.witness.signing_key,
            props=LegacyChainProperties(
                account_creation_fee=self.account_creation_fee or self.witness.props.account_creation_fee,
                maximum_block_size=self.maximum_block_size or self.witness.props.maximum_block_size,
                hbd_interest_rate=hbd_interest_rate,
            ),
        )

    def _create_witness_set_properties_operation(self) -> WitnessSetPropertiesOperation:
        props = iwax.serialize_witness_set_properties(
            key=PublicKey(value=self.witness.signing_key),
            new_signing_key=self.new_signing_key,
            url=self.url,
            hbd_exchange_rate=self.schemas_hbd_exchange_rate,
            account_creation_fee=self.account_creation_fee,
            maximum_block_size=self.maximum_block_size,
            hbd_interest_rate=self.hbd_interest_rate,
            account_subsidy_budget=self.account_subsidy_budget,
            account_subsidy_decay=self.account_subsidy_decay,
        )
        return WitnessSetPropertiesOperation(
            owner=AccountName(self.owner),
            props=props,
        )
