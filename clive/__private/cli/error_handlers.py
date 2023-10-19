from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.exceptions import CLIPrettyError


def register_error_handlers(cli: CliveTyper) -> None:
    @cli.error_handler(Exception)
    def pretty_show_any_error(error: Exception) -> None:
        raise CLIPrettyError(str(error), 1)
