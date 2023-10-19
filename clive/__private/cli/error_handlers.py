import errno

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.abc.command_secured import InvalidPasswordError
from clive.__private.core.commands.activate import WalletDoesNotExistsError
from clive.exceptions import CommunicationError


def register_error_handlers(cli: CliveTyper) -> None:
    @cli.error_handler(Exception)
    def pretty_show_any_error(error: Exception) -> None:
        raise CLIPrettyError(str(error), 1)

    @cli.error_handler(CommunicationError)
    def handle_communication_error(error: CommunicationError) -> None:
        raise CLIPrettyError(str(error), errno.ECOMM) from None

    @cli.error_handler(InvalidPasswordError)
    def handle_invalid_password_error(_: InvalidPasswordError) -> None:
        raise CLIPrettyError("Invalid password.", errno.EINVAL) from None

    @cli.error_handler(WalletDoesNotExistsError)
    def handle_wallet_does_not_exists_error(_: WalletDoesNotExistsError) -> None:
        raise CLIPrettyError("Wallet does not exists.", errno.ENOENT) from None
