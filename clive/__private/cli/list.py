import typer

from clive.__private.cli.common.with_world import WithWorld

list_ = typer.Typer(help="List various things.")


@list_.command()
@WithWorld.decorator(use_beekeeper=False)
def keys(
    ctx: typer.Context,
) -> None:
    """
    List all Public keys stored in the wallet.
    """
    common = WithWorld(**ctx.params)

    assert (
        common.world.profile_data.name == common.profile
    ), f"Wrong profile loaded. {common.world.profile_data.name} != {common.profile}"

    public_keys = common.world.profile_data.working_account.keys

    typer.echo(f"{common.profile}, your keys are:\n{list(public_keys)}")
