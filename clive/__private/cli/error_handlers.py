import errno

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.exceptions import CLIPrettyError, CLIProfileAlreadyExistsError, CLIProfileDoesNotExistsError
from clive.__private.core.commands.abc.command_secured import InvalidPasswordError
from clive.__private.core.commands.activate import WalletDoesNotExistsError
from clive.__private.core.profile_data import ProfileAlreadyExistsError, ProfileDoesNotExistsError
from clive.exceptions import CommunicationError


def register_error_handlers(cli: CliveTyper) -> None:
    @cli.error_handler(Exception)
    def pretty_show_any_error(error: Exception) -> None:
        error_message = str(error)
        message = f"Unhandled exception {type(error).__name__}{f': {error_message}' if error_message else ''}"
        raise CLIPrettyError(message, 1)

    @cli.error_handler(CommunicationError)
    def handle_communication_error(error: CommunicationError) -> None:
        raise CLIPrettyError(str(error), errno.ECOMM) from None

    @cli.error_handler(InvalidPasswordError)
    def handle_invalid_password_error(_: InvalidPasswordError) -> None:
        raise CLIPrettyError("Invalid password.", errno.EINVAL) from None

    @cli.error_handler(WalletDoesNotExistsError)
    def handle_wallet_does_not_exists_error(_: WalletDoesNotExistsError) -> None:
        raise CLIPrettyError("Wallet does not exists.", errno.ENOENT) from None

    @cli.error_handler(ProfileDoesNotExistsError)
    def handle_profile_does_not_exists(error: ProfileDoesNotExistsError) -> None:
        raise CLIProfileDoesNotExistsError(error.profile_name) from None

    @cli.error_handler(ProfileAlreadyExistsError)
    def handle_profile_already_not_exists(error: ProfileAlreadyExistsError) -> None:
        raise CLIProfileAlreadyExistsError(error.profile_name, error.existing_profiles) from None
