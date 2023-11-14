from abc import ABC

from clive.__private.cli.common.perform_transaction_common import PerformTransactionCommon
from clive.__private.cli.exceptions import CLIPrettyError


class OperationCommon(PerformTransactionCommon, ABC):
    """Common options for all commands that perform actions on operations."""

    def _validate_options(self) -> None:
        if self.broadcast and self.sign is None:
            raise CLIPrettyError(
                "You must provide a key alias to sign the transaction with if you want to broadcast them."
            )

        if self.sign is not None and self.password is None:
            raise CLIPrettyError("You must provide a password so wallet can be unlocked while signing a transaction.")

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.world import World  # noqa: F401

        OperationCommon.update_forward_refs(**locals())
