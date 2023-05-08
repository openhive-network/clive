from __future__ import annotations

import signal
import subprocess
import warnings
from pathlib import Path
from subprocess import Popen
from typing import TYPE_CHECKING, TextIO

from clive.__private.config import settings
from clive.__private.logger import logger
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
        self.__files: dict[str, TextIO | None] = {
            "stdout": None,
            "stderr": None,
        }
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

        self.__prepare_files_for_streams(config.wallet_dir)

        self.__pid_file.touch(exist_ok=False)
        self.__process = Popen(
            [self.__executable, "--data-dir", config.wallet_dir.as_posix()],
            stdout=self.__files["stdout"],
            stderr=self.__files["stderr"],
        )
        with self.__pid_file.open(mode="w") as file:
            file.write(f"{self.__process.pid}")

    def close(self) -> None:
        if self.__process is None:
            assert self.__pid_file is None
            return

        self.__process.send_signal(signal.SIGINT)
        try:
            return_code = self.__process.wait(timeout=10)
            logger.debug(f"Beekeeper closed with return code of `{return_code}`.")
        except subprocess.TimeoutExpired:
            self.__process.kill()
            self.__process.wait()
            warnings.warn(
                "Beekeeper process was force-closed with SIGKILL, because didn't close before timeout", stacklevel=2
            )
        self.__close_files_for_streams()

        assert self.__pid_file is not None and self.__pid_file.exists()
        self.__pid_file.unlink()
        self.__pid_file = None
        self.__process = None

    @classmethod
    def get_path_from_settings(cls) -> Path | None:
        path_raw = settings.get("beekeeper.path")
        return Path(path_raw) if path_raw is not None else None

    def __prepare_files_for_streams(self, directory: Path) -> None:
        for name in self.__files:
            path = directory / f"{name}.log"
            self.__files[name] = path.open("w", encoding="utf-8")

    def __close_files_for_streams(self) -> None:
        for name, file in self.__files.items():
            if file is not None:
                file.close()
                self.__files[name] = None
