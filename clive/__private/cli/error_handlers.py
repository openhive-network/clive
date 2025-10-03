from __future__ import annotations

import errno
from typing import TYPE_CHECKING

import beekeepy.exceptions as bke

from clive.__private.cli.exceptions import CLIPrettyError, CLIProfileAlreadyExistsError, CLIProfileDoesNotExistsError
from clive.__private.core.error_handlers.abc.error_notificator import CannotNotifyError
from clive.__private.storage.service.exceptions import ProfileAlreadyExistsError, ProfileDoesNotExistsError
from clive.dev import is_in_dev_mode

if TYPE_CHECKING:
    from clive.__private.cli.clive_typer import CliveTyper


def register_error_handlers(cli: CliveTyper) -> None:
    @cli.error_handler(Exception)
    def pretty_show_any_error(error: Exception) -> None:
        if is_in_dev_mode():
            raise error
        error_message = str(error)
        message = f"Unhandled exception {type(error).__name__}{f': {error_message}' if error_message else ''}"
        raise CLIPrettyError(message, 1)

    @cli.error_handler(bke.CommunicationError)
    def handle_communication_error(error: bke.CommunicationError) -> None:
        raise CLIPrettyError(str(error), errno.ECOMM) from None

    @cli.error_handler(CannotNotifyError)
    def handle_cannot_notify_error(error: CannotNotifyError) -> None:
        raise CLIPrettyError(error.reason, 1) from None

    @cli.error_handler(ProfileDoesNotExistsError)
    def handle_profile_does_not_exists(error: ProfileDoesNotExistsError) -> None:
        raise CLIProfileDoesNotExistsError(error.profile_name) from None

    @cli.error_handler(ProfileAlreadyExistsError)
    def handle_profile_already_not_exists(error: ProfileAlreadyExistsError) -> None:
        raise CLIProfileAlreadyExistsError(error.profile_name, error.existing_profile_names) from None
