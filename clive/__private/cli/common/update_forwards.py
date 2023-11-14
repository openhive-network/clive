from clive.__private.cli.common.operation_common import OperationCommon
from clive.__private.cli.common.perform_transaction_common import PerformTransactionCommon
from clive.__private.cli.common.with_beekeeper import WithBeekeeper
from clive.__private.cli.common.with_profile import WithProfile
from clive.__private.cli.common.with_world import WithWorld
from clive.__private.cli.completion import is_tab_completion_active


def update_forwards() -> None:
    if not is_tab_completion_active():
        OperationCommon.update_forwards()
        PerformTransactionCommon.update_forwards()
        WithBeekeeper.update_forwards()
        WithProfile.update_forwards()
        WithWorld.update_forwards()
