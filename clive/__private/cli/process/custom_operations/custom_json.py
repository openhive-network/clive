import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import OperationOptionsGroup, modified_param, options

custom_json = CliveTyper(name="custom-json", help="Send raw custom json operation.")


@custom_json.callback(param_groups=[OperationOptionsGroup], invoke_without_command=True)
async def process_custom_json(
    ctx: typer.Context,  # noqa: ARG001
    authorize: list[str] = modified_param(
        options.working_account_list_template,
        param_decls=("--authorize",),
        help="Posting authorities. Option can be added multiple times. If neither authorize nor authorize-by-active is"
        " used, then posting authority of working account is used for authorization.",
    ),
    authorize_by_active: list[str] = typer.Option(
        [],
        help="Active authorities. Option can be added multiple times. If neither authorize nor authorize-by-active is"
        " used, then posting authority of working account is used for authorization.",
    ),
    id_: str = typer.Option(
        ...,
        "--id",
        help="Custom identifier that allows filtering of custom json operations.",
        show_default=False,
    ),
    json_: str = typer.Option(
        ...,
        "--json",
        help="Custom json content. This can be a path to a file or a string itself.",
        show_default=False,
    ),
) -> None:
    """Send custom json operation, json can be provided as string or file."""
    from clive.__private.cli.commands.process.process_custom_json import ProcessCustomJson

    common = OperationOptionsGroup.get_instance()
    operation = ProcessCustomJson(
        **common.as_dict(),
        id_=id_,
        authorize_by_active=authorize_by_active,
        authorize=authorize,
        json_or_path=json_,
    )
    await operation.run()
