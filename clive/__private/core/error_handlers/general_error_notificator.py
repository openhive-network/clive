from __future__ import annotations

from typing import TYPE_CHECKING, Final, TypeGuard

import beekeepy.exceptions as bke

from clive.__private.core.commands.build_transaction import TransactionWaxValidationError
from clive.__private.core.commands.recover_wallets import CannotRecoverWalletsError
from clive.__private.core.commands.save_profile import ProfileSavingFailedError
from clive.__private.core.error_handlers.abc.error_notificator import ErrorNotificator
from clive.__private.storage.service.exceptions import ProfileEncryptionError

if TYPE_CHECKING:
    from collections.abc import Callable

INVALID_PASSWORD_MESSAGE: Final[str] = "The password you entered is incorrect. Please try again."  # noqa: S105


class GeneralErrorNotificator(ErrorNotificator[Exception]):
    """
    A context manager that notifies about any catchable errors that are not handled by other notificators.

    Attributes:
        SEARCHED_AND_PRINTED_MESSAGES: A mapping of exception types to messages that should be printed.
    """

    SEARCHED_AND_PRINTED_MESSAGES: Final[dict[type[Exception], str | Callable[[Exception], str]]] = {
        bke.InvalidPasswordError: INVALID_PASSWORD_MESSAGE,
        bke.NoWalletWithSuchNameError: "Wallet with this name was not found on the beekeeper. Please try again.",
        bke.NotExistingKeyError: "Key does not exist in the wallet.",
        ProfileEncryptionError: "Profile encryption failed which means profile cannot be saved or loaded.",
        CannotRecoverWalletsError: CannotRecoverWalletsError.MESSAGE,
        ProfileSavingFailedError: ProfileSavingFailedError.MESSAGE,
        TransactionWaxValidationError: lambda error: (
            f"Transaction validation failed. Wax error details:\n{error.wax_error_details}"  # type: ignore[attr-defined]
        ),
    }

    def __init__(self) -> None:
        super().__init__()
        self._message_to_print = "Something went wrong. Please try again."

    def _is_exception_to_catch(self, error: Exception) -> TypeGuard[Exception]:
        for searched, printed in self.SEARCHED_AND_PRINTED_MESSAGES.items():
            if type(error) is searched:
                self._message_to_print = printed if isinstance(printed, str) else printed(error)
                return True
        return False

    def _determine_message(self, _: Exception) -> str:
        return self._message_to_print
