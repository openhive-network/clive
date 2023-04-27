from __future__ import annotations

from pathlib import Path
from signal import SIGINT
from subprocess import Popen, TimeoutExpired
from typing import TYPE_CHECKING, TextIO

from clive.__private.config import settings
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.config import BeekeeperConfig


class BeekeeperAlreadyRunningError(Exception):
    pass


class BeekeeperNotificationServerNotConfiguredError(CliveError):
    pass


class BeekeeperNonZeroExitCodeError(CliveError):
    pass


class BeekeeperDidNotClosedError(CliveError):
    pass


class BeekeeperNotConfiguredError(CliveError):
    pass


class BeekeeperExecutable:
    def __init__(self) -> None:
        self.__executable: Path = self.get_path_from_settings()  # type: ignore
        if self.__executable is None:
            raise BeekeeperNotConfiguredError()

        self.__process: Popen[bytes] | None = None
        self.__stderr: TextIO | None = None
        self.__stdout: TextIO | None = None
        self.__pid_file: Path | None = None

    def run(self, config: BeekeeperConfig) -> None:
        if self.__process is not None:
            raise BeekeeperAlreadyRunningError()

        if config.notifications_endpoint is None:
            raise BeekeeperNotificationServerNotConfiguredError()

        # prepare config
        self.__pid_file = config.wallet_dir / "beekeeper.pid"
        if not config.wallet_dir.exists():
            config.wallet_dir.mkdir()
        elif self.__pid_file.exists():
            raise BeekeeperAlreadyRunningError(self.__pid_file)
        config_filename = config.wallet_dir / "config.ini"
        config.save(config_filename)

        # prepare output
        self.__stdout = (config.wallet_dir / "stdout.log").open("wt", encoding="utf-8")
        self.__stderr = (config.wallet_dir / "stderr.log").open("wt", encoding="utf-8")

        self.__pid_file.touch(exist_ok=False)
        self.__process = Popen[bytes](
            [self.__executable, "--data-dir", config.wallet_dir.as_posix()],
            stdout=self.__stdout,
            stderr=self.__stderr,
        )
        with self.__pid_file.open(mode="w") as file:
            file.write(f"{self.__process.pid}")

    def close(self) -> None:
        if self.__process is None:
            assert self.__pid_file is None
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

            assert self.__pid_file is not None and self.__pid_file.exists()
            self.__pid_file.unlink()
            self.__pid_file = None

    @classmethod
    def get_path_from_settings(cls) -> Path | None:
        path_raw = settings.get("beekeeper.path")
        return Path(path_raw) if path_raw is not None else None
