from __future__ import annotations

from signal import SIGINT
from subprocess import Popen
from typing import TYPE_CHECKING, Final, TextIO

from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper.config import BeekeeperConfig


class BeekeeperExecutable:
    class BeekeeperAlreadyRunningError(Exception):
        pass

    class BeekeeperNotificationServerNotConfiguredError(CliveError):
        pass

    class BeekeeperNonZeroExitCodeError(CliveError):
        pass

    DEFAULT_EXECUTABLE_PATH: Final[str] = "./beekeeper"

    def __init__(self, *, executable: Path | None = None) -> None:
        self.__executable = executable or self.DEFAULT_EXECUTABLE_PATH
        self.__process: Popen | None = None  # type: ignore
        self.__stderr: TextIO | None = None
        self.__stdout: TextIO | None = None

    def run(self, config: BeekeeperConfig) -> None:
        if self.__process is not None:
            raise BeekeeperExecutable.BeekeeperAlreadyRunningError()

        if config.notifications_endpoint is None:
            raise BeekeeperExecutable.BeekeeperNotificationServerNotConfiguredError()

        # prepare config
        if not config.wallet_dir.exists():
            config.wallet_dir.mkdir()
        config_filename = config.wallet_dir / "config.ini"
        config.save(config_filename)

        # prepare output
        self.__stdout = (config.wallet_dir / "stdout.log").open("wt", encoding="utf-8")
        self.__stderr = (config.wallet_dir / "stderr.log").open("wt", encoding="utf-8")

        self.__process = Popen[str](
            [self.__executable, "--data-dir", config.wallet_dir.as_posix()],
            stdout=self.__stdout,
            stderr=self.__stderr,
        )

    def close(self) -> None:
        if self.__process is None:
            return

        def wait_for_kill() -> None:
            if self.__process is not None and self.__process.wait(5.0) != 0:
                raise BeekeeperExecutable.BeekeeperNonZeroExitCodeError()

        try:
            self.__process.send_signal(SIGINT)
            wait_for_kill()
        except TimeoutError:
            self.__process.kill()
            wait_for_kill()
        finally:
            if self.__stderr is not None:
                self.__stderr.close()
            if self.__stdout is not None:
                self.__stdout.close()
            self.__process = None
