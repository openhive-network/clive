from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, override

from clive.__private.cli.commands.abc.operation_command import OperationCommand
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
    Witness,
    WitnessSetPropertiesOperation,
    WitnessUpdateOperation,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.__private.cli.types import ComposeTransaction


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
            "You can skip the '--use-active-authority' option or explicitly use '--use-witness-key'."
        )


@dataclass(kw_only=True)
class ProcessUpdateWitness(OperationCommand):
    owner: str
    use_witness_key: bool
    account_creation_fee: Asset.Hive | None
    maximum_block_size: int | None
    hbd_interest_rate: Decimal | None
    account_subsidy_budget: int | None
    account_subsidy_decay: int | None
    new_signing_key: PublicKey | None
    hbd_exchange_rate: Asset.Hbd | None
    url: str | None

    _witness: Witness | None = field(init=False, default=None)

    @property
    def use_active_authority(self) -> bool:
        return not self.use_witness_key

    @property
    def witness_ensure(self) -> Witness:
        assert self._witness, "Witness data was not fetched yet"
        return self._witness

    @override
    async def fetch_data(self) -> None:
        try:
            self._witness = (await self.world.commands.find_witness(witness_name=self.owner)).result_or_raise
        except WitnessNotFoundError as err:
            raise CLIWitnessNotFoundError(self.owner) from err

    @override
    async def _create_operations(self) -> ComposeTransaction:
        if self._needs_feed_publish_operation:
            yield self._create_feed_publish_operation()
        if self._needs_witness_update_operation:
            yield self._create_witness_update_operation()
        if self._needs_witness_set_properties_operation:
            yield self._create_witness_set_properties_operation()

    @override
    async def validate(self) -> None:
        self._validate_requirements_for_witness_set_propertues_operation()
        self._validate_not_empty()
        await super().validate()

    def _validate_not_empty(self) -> None:
        is_operation_required = any(
            [
                self._needs_feed_publish_operation,
                self._needs_witness_update_operation,
                self._needs_witness_set_properties_operation,
            ]
        )
        if not is_operation_required:
            raise CLIPrettyError(
                "Transaction with no changes to witness cannot be created. Use '--help' flag to display help."
            )

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
        return self.use_witness_key and are_witness_set_properties_options_required

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
        assert self.hbd_exchange_rate is not None, (
            "Feed publish should be created only if command requires changing hbd_exchange_rate"
        )
        return FeedPublishOperation(
            publisher=AccountName(self.owner),
            exchange_rate=HbdExchangeRate(base=self.hbd_exchange_rate, quote=Asset.hive(1)),
        )

    def _create_witness_update_operation(self) -> WitnessUpdateOperation:
        witness = self.witness_ensure
        # TODO: remove those 3 assertions after https://gitlab.syncad.com/hive/schemas/-/issues/46 is fixed
        assert witness.props.account_creation_fee is not None, "Account creation fee must is always set"
        assert witness.props.maximum_block_size is not None, "Maximum block size is always set"
        assert witness.props.hbd_interest_rate is not None, "Hbd interest rate is always set"
        hbd_interest_rate = (
            percent_to_hive_percent(self.hbd_interest_rate)
            if self.hbd_interest_rate
            else witness.props.hbd_interest_rate
        )
        return WitnessUpdateOperation(
            owner=AccountName(self.owner),
            url=self.url or witness.url,
            block_signing_key=self.new_signing_key.value if self.new_signing_key else witness.signing_key,
            props=LegacyChainProperties(
                account_creation_fee=self.account_creation_fee or witness.props.account_creation_fee,
                maximum_block_size=self.maximum_block_size or witness.props.maximum_block_size,
                hbd_interest_rate=hbd_interest_rate,
            ),
        )

    def _create_witness_set_properties_operation(self) -> WitnessSetPropertiesOperation:
        wax_operation_wrapper = iwax.WitnessSetPropertiesWrapper.create(
            owner=self.owner,
            key=PublicKey(value=self.witness_ensure.signing_key),
            new_signing_key=self.new_signing_key,
            account_creation_fee=self.account_creation_fee,
            url=self.url,
            hbd_exchange_rate=self.hbd_exchange_rate,
            maximum_block_size=self.maximum_block_size,
            hbd_interest_rate=self.hbd_interest_rate,
            account_subsidy_budget=self.account_subsidy_budget,
            account_subsidy_decay=self.account_subsidy_decay,
        )
        return wax_operation_wrapper.to_schemas(self.world.wax_interface)
