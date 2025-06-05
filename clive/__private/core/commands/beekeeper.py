from __future__ import annotations

from dataclasses import dataclass

from beekeepy import find_running_beekeepers

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.settings import safe_settings


@dataclass
class IsBeekeeperRunningResult:
    is_running: bool
    pid: int | None = None

    @property
    def pid_ensure(self) -> int:
        assert self.pid is not None, "pid is not set."
        return self.pid


@dataclass(kw_only=True)
class IsBeekeeperRunning(CommandWithResult[IsBeekeeperRunningResult]):
    async def _execute(self) -> None:
        beekeeper_working_directory = safe_settings.beekeeper.working_directory
        running_beekeepers = find_running_beekeepers(cwd=beekeeper_working_directory)

        if running_beekeepers:
            assert len(running_beekeepers) == 1, "More beekeepers are running than expected."
            running_beekeeper = running_beekeepers[0]
            self._result = IsBeekeeperRunningResult(is_running=True, pid=running_beekeeper.pid)
        else:
            self._result = IsBeekeeperRunningResult(is_running=False)
