from clive.__private.cli.common.operation_common import OperationCommon
from clive.__private.cli.common.with_beekeeper import WithBeekeeper
from clive.__private.cli.common.with_world import WithWorld
from clive.__private.util import is_tab_completion_active


def update_forwards() -> None:
    if not is_tab_completion_active():
        WithBeekeeper.update_forwards()
        WithWorld.update_forwards()
        OperationCommon.update_forwards()
