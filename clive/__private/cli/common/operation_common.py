from abc import ABC

from clive.__private.cli.common.perform_transaction_common import PerformTransactionCommon


class OperationCommon(PerformTransactionCommon, ABC):
    """Common options for all commands that perform actions on operations."""

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.world import World  # noqa: F401

        OperationCommon.update_forward_refs(**locals())
