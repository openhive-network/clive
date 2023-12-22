import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationCommonOptions, options

proxy = CliveTyper(name="proxy", help="Set, change or remove a proxy.")


@proxy.command(name="set", common_options=[OperationCommonOptions])
async def process_proxy_set(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
    proxy: str = typer.Option(..., help="Name of new proxy account."),
) -> None:
    """Sets proxy or changes existing proxy."""
    from clive.__private.cli.commands.process.process_proxy_set import ProcessProxySet

    operation_common = OperationCommonOptions.get_instance()
    await ProcessProxySet(
        **operation_common.as_dict(),
        account_name=account_name,
        proxy=proxy,
    ).run()


@proxy.command(name="clear", common_options=[OperationCommonOptions])
async def process_proxy_clear(
    ctx: typer.Context,  # noqa: ARG001
    account_name: str = options.account_name_option,
) -> None:
    """Removes proxy."""
    from clive.__private.cli.commands.process.process_proxy_clear import ProcessProxyClear

    operation_common = OperationCommonOptions.get_instance()
    await ProcessProxyClear(**operation_common.as_dict(), account_name=account_name).run()
