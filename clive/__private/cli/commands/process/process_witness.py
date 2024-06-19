from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core import iwax
from clive.__private.core.constants.node import NULL_ACCOUNT_KEY_VALUE
from schemas.fields.assets.hive import AssetHiveHF26
from schemas.fields.basic import PublicKey
from clive.models.aliased import LegacyChainProperties, WitnessProps
from clive.models.aliased import CurrentPriceFeed
from schemas.operations import FeedPublishOperation, WitnessSetPropertiesOperation, WitnessUpdateOperation


if TYPE_CHECKING:
    from clive.models import Asset


@dataclass(kw_only=True)
class ProcessWitnessCreate(OperationCommand):
    owner: str
    url: str
    block_signing_key: PublicKey
    fee: Asset.Hive
    account_creation_fee: Asset.Hive
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> WitnessUpdateOperation:
        props = LegacyChainProperties(account_creation_fee=self.account_creation_fee)

        return WitnessUpdateOperation(
            owner=self.owner, url=self.url, block_signing_key=self.block_signing_key, fee=self.fee, props=props
        )


@dataclass(kw_only=True)
class ProcessWitnessDisable(OperationCommand):
    owner: str
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> WitnessSetPropertiesOperation:
        null_key = PublicKey(NULL_ACCOUNT_KEY_VALUE)
        import typer

        typer.echo(f"{null_key=}")
        try:
            witness = (await self.world.commands.find_witness(witness_name=self.owner)).result_or_raise
        except AssertionError as error:
            raise CLIPrettyError(f"Account `{self.owner}` is not witness") from error

        signing_key = witness.signing_key

        typer.echo(f"{signing_key=}")
        if signing_key == NULL_ACCOUNT_KEY_VALUE:
            raise CLIPrettyError(f"Witness `{self.owner}` is already disabled")

        props = WitnessProps(
            new_signing_key=NULL_ACCOUNT_KEY_VALUE,
        )
        props_serialized = iwax.serialize_witness_set_properties(key=signing_key, props=props)

        return WitnessSetPropertiesOperation(owner=self.owner, props=props_serialized)


@dataclass(kw_only=True)
class ProcessWitnessFeedPublish(OperationCommand):
    exchange_rate: CurrentPriceFeed
    publisher: str
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> WitnessUpdateOperation:
        props = LegacyChainProperties()
        return FeedPublishOperation(
            exchange_rate=self.exchange_rate,
            publisher=self.publisher
        )


@dataclass(kw_only=True)
class ProcessWitnessUpdate(OperationCommand):
    owner: str
    props: WitnessProps

    async def _create_operation(self) -> WitnessSetPropertiesOperation:
        import typer

        witness = (await self.world.commands.find_witness(witness_name=self.owner)).result_or_raise
        signing_key = witness.signing_key

        typer.echo(f"{signing_key=}")
        typer.echo(f"{self.props=}")

        props_serialized = iwax.serialize_witness_set_properties(key=signing_key, props=self.props)
        return WitnessSetPropertiesOperation(owner=self.owner, props=props_serialized)
