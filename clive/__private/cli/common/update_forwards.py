from clive.__private.cli.common.operation_common import OperationCommon
from clive.__private.cli.common.with_world import WithWorld
from clive.__private.cli.completion import is_tab_completion_active


def update_forwards() -> None:
    if not is_tab_completion_active():
        WithWorld.update_forwards()
        OperationCommon.update_forwards()
