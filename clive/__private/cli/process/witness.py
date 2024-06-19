from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options
from clive.__private.cli.common.parsers import hive_asset

if TYPE_CHECKING:
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
    from clive.__private.cli.commands.process.process_witness_create import ProcessWitnessCreate
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
    from clive.__private.cli.commands.process.process_witness_disable import ProcessWitnessDisable

    common = OperationCommonOptions.get_instance()
    await ProcessWitnessDisable(**common.as_dict(), owner=owner).run()


@witness.command(name="update", common_options=[OperationCommonOptions])
async def process_witness_update(
    ctx: typer.Context,  # noqa: ARG001
    owner: str = options.account_name_option,
) -> None:
    """Update witness properties."""
    from clive.__private.cli.commands.process.process_witness_update import ProcessWitnessUpdate

    common = OperationCommonOptions.get_instance()
    await ProcessWitnessUpdate(**common.as_dict(), owner=owner).run()
