from __future__ import annotations

from signal import SIGINT
from subprocess import Popen, TimeoutExpired
from typing import TYPE_CHECKING, Final, TextIO

from clive.exceptions import CliveError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper.config import BeekeeperConfig


class BeekeeperAlreadyRunningError(Exception):
    pass


class BeekeeperNotificationServerNotConfiguredError(CliveError):
    pass


class BeekeeperNonZeroExitCodeError(CliveError):
    pass


class BeekeeperDidNotClosedError(CliveError):
    pass


class BeekeeperExecutable:
    DEFAULT_EXECUTABLE_PATH: Final[str] = "./beekeeper"

    def __init__(self, *, executable: Path | None = None) -> None:
        self.__executable = executable or self.DEFAULT_EXECUTABLE_PATH
        self.__process: Popen | None = None  # type: ignore
        self.__stderr: TextIO | None = None
        self.__stdout: TextIO | None = None
        self.__lock_file: Path | None = None

    def run(self, config: BeekeeperConfig) -> None:
        if self.__process is not None:
            raise BeekeeperAlreadyRunningError()

        if config.notifications_endpoint is None:
            raise BeekeeperNotificationServerNotConfiguredError()

        # prepare config
        self.__lock_file = config.wallet_dir / "__lock"
        if not config.wallet_dir.exists():
            config.wallet_dir.mkdir()
        elif self.__lock_file.exists():
            raise BeekeeperAlreadyRunningError(self.__lock_file)
        config_filename = config.wallet_dir / "config.ini"
        config.save(config_filename)

        # prepare output
        self.__stdout = (config.wallet_dir / "stdout.log").open("wt", encoding="utf-8")
        self.__stderr = (config.wallet_dir / "stderr.log").open("wt", encoding="utf-8")

        self.__lock_file.touch(exist_ok=False)
        self.__process = Popen[str](
            [self.__executable, "--data-dir", config.wallet_dir.as_posix()],
            stdout=self.__stdout,
            stderr=self.__stderr,
        )

    def close(self) -> None:
        if self.__process is None:
            assert self.__lock_file is None
            return

        def wait_for_kill() -> None:
            if self.__process is not None and self.__process.wait(5.0) != 0:
                raise BeekeeperNonZeroExitCodeError()

        try:
            self.__process.send_signal(SIGINT)
            wait_for_kill()
        except TimeoutExpired:
            try:
                self.__process.kill()
                wait_for_kill()
            except TimeoutExpired:
                try:
                    self.__process.terminate()
                    wait_for_kill()
                except TimeoutError as e:
                    raise BeekeeperDidNotClosedError() from e
        finally:
            if self.__stderr is not None:
                self.__stderr.close()
            if self.__stdout is not None:
                self.__stdout.close()
            self.__process = None

            assert self.__lock_file is not None and self.__lock_file.exists()
            self.__lock_file.unlink()
            self.__lock_file = None
