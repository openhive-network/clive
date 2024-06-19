from typing import Optional, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options
from clive.__private.cli.common.parsers import hive_asset
from clive.models import Asset

witness = CliveTyper(name="witness", help="Become witness, update witness properties.")


@witness.command(name="create", common_options=[OperationCommonOptions])
async def process_witness_create(  # noqa: PLR0913
    ctx: typer.Context,  # noqa: ARG001
    owner: str = options.account_name_option,
    url: str = typer.Option(
        ...,
        help="Website URL.",
    ),
    block_signing_key: str = typer.Option(
        ...,
        help="Public key used to sign blocks by this witness.",
    ),
    fee: str = typer.Option(
        ...,
        parser=hive_asset,
        help="The fee paid to register a new witness, should be 10x current block production pay.",
    ),
    account_creation_fee: str = typer.Option(
        ...,
        parser=hive_asset,
        help="Account creation fee proposed by this witness.",
    ),
) -> None:
    """Become witness."""
    from clive.__private.cli.commands.process.process_witness import ProcessWitnessCreate
    from schemas.fields.basic import PublicKey

    block_signing_key_ = PublicKey(block_signing_key)
    fee_ = cast("Asset.Hive", fee)
    account_creation_fee_ = cast("Asset.Hive", account_creation_fee)
    common = OperationCommonOptions.get_instance()
    await ProcessWitnessCreate(
        **common.as_dict(),
        owner=owner,
        url=url,
        block_signing_key=block_signing_key_,
        fee=fee_,
        account_creation_fee=account_creation_fee_,
    ).run()


@witness.command(name="disable", common_options=[OperationCommonOptions])
async def process_witness_disable(
    ctx: typer.Context,  # noqa: ARG001
    owner: str = options.account_name_option,
) -> None:
    """Stop being witness."""
    from clive.__private.cli.commands.process.process_witness import ProcessWitnessDisable

    common = OperationCommonOptions.get_instance()
    await ProcessWitnessDisable(**common.as_dict(), owner=owner).run()


@witness.command(name="feed-publish", common_options=[OperationCommonOptions])
async def process_witness_feed_publish(
    ctx: typer.Context,  # noqa: ARG001
    exchange_rate: float,
    publisher: str = options.account_name_option,
) -> None:
    """Publish exchange rate of hive/hbd."""
    from clive.__private.cli.commands.process.process_witness import ProcessWitnessFeedPublish
    from clive.models.aliased import CurrentPriceFeed

    exchange_rate_ = (
        CurrentPriceFeed(quote=Asset.hbd(1) * exchange_rate, base=Asset.hive(1))
    )

    common = OperationCommonOptions.get_instance()
    await ProcessWitnessFeedPublish(**common.as_dict(), exchange_rate=exchange_rate_, publisher=publisher).run()


@witness.command(name="update", common_options=[OperationCommonOptions])
async def process_witness_update(
    ctx: typer.Context,  # noqa: ARG001
    owner: str = options.account_name_option,
    account_creation_fee: Optional[str] = typer.Option(
        None,
        parser=hive_asset,
        help="Updated fee for creating new account. (e.g. 2.500 HIVE)",
    ),
    maximum_block_size: Optional[int] = None,
    hbd_interest_rate: Optional[int] = None,
    account_subsidy_budget: Optional[int] = None,
    account_subsidy_decay: Optional[int] = None,
    hbd_exchange_rate: Optional[float] = None,
    url: Optional[str] = None,
    new_signing_key: Optional[str] = None,
) -> None:
    """Update witness properties."""
    from clive.__private.cli.commands.process.process_witness import ProcessWitnessUpdate
    from clive.models.aliased import CurrentPriceFeed
    from clive.models.aliased import LegacyChainProperties, WitnessProps

    account_creation_fee_ = cast("Asset.Hive", account_creation_fee) if account_creation_fee else None
    hbd_exchange_rate_ = (
        CurrentPriceFeed(quote=Asset.hbd(1) * hbd_exchange_rate, base=Asset.hive(1)) if hbd_exchange_rate else None
    )
    props = WitnessProps(
        account_creation_fee=account_creation_fee_,
        maximum_block_size=maximum_block_size,
        hbd_interest_rate=hbd_interest_rate,
        account_subsidy_budget=account_subsidy_budget,
        account_subsidy_decay=account_subsidy_decay,
        hbd_exchange_rate=hbd_exchange_rate_,
        url=url,
        new_signing_key=new_signing_key,
    )

    common = OperationCommonOptions.get_instance()
    await ProcessWitnessUpdate(
        **common.as_dict(),
        owner=owner,
        props=props,
    ).run()
