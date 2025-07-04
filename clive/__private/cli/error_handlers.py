from __future__ import annotations

import errno
from typing import TYPE_CHECKING

from beekeepy.exceptions import CommunicationError

from clive.__private.cli.exceptions import CLIPrettyError, CLIProfileAlreadyExistsError, CLIProfileDoesNotExistsError
from clive.__private.core.error_handlers.abc.error_notificator import CannotNotifyError
from clive.__private.storage.service import ProfileAlreadyExistsError, ProfileDoesNotExistsError
from clive.dev import is_in_dev_mode

if TYPE_CHECKING:
    from clive.__private.cli.clive_typer import CliveTyper


def register_error_handlers(cli: CliveTyper) -> None:
    """
    Register error handlers for the CLI.

    This function registers custom error handlers for various exceptions that may occur during the execution of the
    CLI commands.

    Args:
        cli: The CLI application instance to register the error handlers with.

    Returns:
        None
    """

    @cli.error_handler(Exception)
    def pretty_show_any_error(error: Exception) -> None:
        """
        Handle any unhandled exception.

        Args:
            error: The exception that was raised.

        Raises:
            CLIPrettyError: A formatted error message for the CLI.

        Returns:
            None
        """
        if is_in_dev_mode():
            raise error
        error_message = str(error)
        message = f"Unhandled exception {type(error).__name__}{f': {error_message}' if error_message else ''}"
        raise CLIPrettyError(message, 1)

    @cli.error_handler(CommunicationError)
    def handle_communication_error(error: CommunicationError) -> None:
        """
        Handle communication errors that occur during CLI operations.

        Args:
            error: The CommunicationError that was raised.

        Raises:
            CLIPrettyError: A formatted error message for the CLI.

        Returns:
            None
        """
        raise CLIPrettyError(str(error), errno.ECOMM) from None

    @cli.error_handler(CannotNotifyError)
    def handle_cannot_notify_error(error: CannotNotifyError) -> None:
        """
        Handle errors that occur when the CLI cannot notify the user.

        Args:
            error: The CannotNotifyError that was raised.

        Raises:
            CLIPrettyError: A formatted error message for the CLI.

        Returns:
            None
        """
        raise CLIPrettyError(error.reason, 1) from None

    @cli.error_handler(ProfileDoesNotExistsError)
    def handle_profile_does_not_exists(error: ProfileDoesNotExistsError) -> None:
        """
        Handle errors when a profile does not exist.

        Args:
            error: The ProfileDoesNotExistsError that was raised.

        Raises:
            CLIProfileDoesNotExistsError: A formatted error message for the CLI indicating the profile does not exist.

        Returns:
            None
        """
        raise CLIProfileDoesNotExistsError(error.profile_name) from None

    @cli.error_handler(ProfileAlreadyExistsError)
    def handle_profile_already_not_exists(error: ProfileAlreadyExistsError) -> None:
        """
        Handle errors when a profile already exists.

        Args:
            error: The ProfileAlreadyExistsError that was raised.

        Raises:
            CLIProfileAlreadyExistsError: A formatted error message for the CLI indicating the profile already exists.

        Returns:
            None
        """
        raise CLIProfileAlreadyExistsError(error.profile_name, error.existing_profile_names) from None
