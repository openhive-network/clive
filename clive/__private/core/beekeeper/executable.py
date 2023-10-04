from __future__ import annotations

import json
import os
import signal
import subprocess
import time
import warnings
from pathlib import Path
from subprocess import Popen
from typing import TextIO

from clive.__private.config import settings
from clive.__private.core.beekeeper.config import BeekeeperConfig
from clive.__private.core.beekeeper.exceptions import (
    BeekeeperAlreadyRunningError,
    BeekeeperNotConfiguredError,
    BeekeeperNotificationServerNotConfiguredError,
    BeekeeperNotRunningError,
    BeekeeperTimeoutError,
)
from clive.__private.logger import logger


class BeekeeperExecutable:
    def __init__(self, config: BeekeeperConfig, *, run_in_background: bool = False) -> None:
        self.__config = config
        self.__executable: Path = self.get_path_from_settings()  # type: ignore
        if self.__executable is None:
            raise BeekeeperNotConfiguredError

        self.__run_in_background = run_in_background
        self.__process: Popen[bytes] | None = None
        self.__files: dict[str, TextIO | None] = {
            "stdout": None,
            "stderr": None,
        }

    @property
    def pid(self) -> int:
        if self.__process is None:
            return self.get_pid_from_file()
        return self.__process.pid

    @classmethod
    def get_pid_from_file(cls) -> int:
        pid_file = cls.__get_pid_file_path()
        if not pid_file.is_file():
            raise BeekeeperNotRunningError("Cannot get PID, Beekeeper is not running.")

        with pid_file.open("r") as file:
            data = json.load(file)

        return int(data["pid"])

    @classmethod
    def is_already_running(cls) -> bool:
        try:
            cls.get_pid_from_file()
        except BeekeeperNotRunningError:
            return False
        else:
            return True

    def run(self) -> None:
        if self.__process is not None:
            raise BeekeeperAlreadyRunningError

        if self.__config.notifications_endpoint is None:
            raise BeekeeperNotificationServerNotConfiguredError

        # prepare config
        if not self.__config.wallet_dir.exists():
            self.__config.wallet_dir.mkdir()
        config_filename = self.__config.wallet_dir / "config.ini"
        self.__config.save(config_filename)

        self.__prepare_files_for_streams(self.__config.wallet_dir)

        command = ["nohup"] if self.__run_in_background else []
        command += [str(self.__executable.absolute())]
        command += ["--data-dir", self.__config.wallet_dir.as_posix()]

        try:
            self.__process = Popen(
                command,
                stdout=self.__files["stdout"],
                stderr=self.__files["stderr"],
                preexec_fn=os.setpgrp,  # create new process group, so signals won't be passed to child process
            )
        except Exception as e:
            logger.debug(f"Caught exception during start, closing: {e}")
            self.close()
            raise e from e

    def close(self, *, wait_for_deleted_pid: bool = True) -> None:
        if self.__process is None:
            self.__close_files_for_streams()
            return

        try:
            self.__process.send_signal(signal.SIGINT)
            return_code = self.__process.wait(timeout=10)
            logger.debug(f"Beekeeper closed with return code of `{return_code}`.")
        except subprocess.TimeoutExpired:
            self.__process.kill()
            self.__process.wait()

            message = "Beekeeper process was force-closed with SIGKILL, because didn't close before timeout"
            logger.error(message)
            warnings.warn(message, stacklevel=2)
        finally:
            self.__close_files_for_streams()
            self.__process = None
            if wait_for_deleted_pid:
                self.__wait_for_pid_file_to_be_deleted()

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

    def __wait_for_pid_file_to_be_deleted(self, *, timeout_secs: float = 10.0) -> None:
        pid_file = self.__get_pid_file_path()
        start_time = time.perf_counter()
        while pid_file.exists():
            if time.perf_counter() - start_time > timeout_secs:
                message = f"Beekeeper PID file was NOT deleted in {timeout_secs} seconds."
                logger.error(message)
                raise BeekeeperTimeoutError(message)
            time.sleep(0.1)
        logger.debug(f"Beekeeper PID file was deleted in {time.perf_counter() - start_time:.2f} seconds.")

    @staticmethod
    def __get_pid_file_path() -> Path:
        return BeekeeperConfig.get_wallet_dir() / "beekeeper.pid"
