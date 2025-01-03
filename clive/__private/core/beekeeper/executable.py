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

from clive.__private.core.beekeeper.command_line_args import BeekeeperCLIArguments
from clive.__private.core.beekeeper.config import BeekeeperConfig
from clive.__private.core.beekeeper.defaults import BeekeeperDefaults
from clive.__private.core.beekeeper.exceptions import (
    BeekeeperAlreadyRunningError,
    BeekeeperNotConfiguredError,
    BeekeeperNotificationServerNotConfiguredError,
    BeekeeperNotRunningError,
    BeekeeperTimeoutError,
)
from clive.__private.logger import logger
from clive.__private.settings import safe_settings


class BeekeeperExecutable:
    def __init__(
        self,
        config: BeekeeperConfig,
        *,
        run_in_background: bool = False,
    ) -> None:
        self.__config = config
        self.__executable: Path = self.get_path_from_settings()  # type: ignore[assignment]
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

    def prepare_command(self, *, arguments: BeekeeperCLIArguments | None = None) -> list[str]:
        command = ["nohup"] if self.__run_in_background else []
        command += [str(self.__executable.absolute())]

        if arguments:
            if arguments.notifications_endpoint and arguments.notifications_endpoint.port is None:
                arguments.notifications_endpoint = self.__config.notifications_endpoint
            if not arguments.data_dir or arguments.data_dir == Path().home() / ".beekeeper":
                # We set default value for arguments.data_dir to home dir (mostly for documenting) but we should not
                # pollute it during tests.
                arguments.data_dir = self.__config.wallet_dir
            command += arguments.process()
        else:
            arguments = BeekeeperCLIArguments()
            arguments.data_dir = self.__config.wallet_dir
            command += arguments.process()
        return command

    def pre_run_preparation(
        self, *, allow_empty_notification_server: bool = False, arguments: BeekeeperCLIArguments | None = None
    ) -> list[str]:
        if self.__process is not None:
            raise BeekeeperAlreadyRunningError

        if not allow_empty_notification_server and self.__config.notifications_endpoint is None:
            raise BeekeeperNotificationServerNotConfiguredError

        # prepare config
        if (
            arguments
            and arguments.wallet_dir is not None
            and arguments.wallet_dir != BeekeeperDefaults.DEFAULT_WALLET_DIR
        ):
            self.__config.wallet_dir = arguments.wallet_dir
        if not self.__config.wallet_dir.exists():
            self.__config.wallet_dir.mkdir()
        if arguments and not arguments.dump_config:
            config_filename = self.__config.wallet_dir / "config.ini"
            self.__config.save(config_filename)
        if allow_empty_notification_server and (arguments and arguments.notifications_endpoint):
            self.__config.notifications_endpoint = arguments.notifications_endpoint

        return self.prepare_command(arguments=arguments)

    def run_and_get_output(
        self,
        *,
        allow_empty_notification_server: bool = False,
        timeout: float = 3.0,
        arguments: BeekeeperCLIArguments | None = None,
    ) -> str:
        command = self.pre_run_preparation(
            allow_empty_notification_server=allow_empty_notification_server, arguments=arguments
        )
        logger.debug(f"Executing beekeeper: {command}")
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=timeout)
        return result.decode("utf-8").strip()

    def run(
        self, *, allow_empty_notification_server: bool = False, arguments: BeekeeperCLIArguments | None = None
    ) -> None:
        command = self.pre_run_preparation(
            allow_empty_notification_server=allow_empty_notification_server, arguments=arguments
        )
        self.__prepare_files_for_streams(self.__config.wallet_dir)
        logger.debug(f"Executing beekeeper: {command}")
        try:
            self.__process = Popen(
                command,
                stdout=self.__files["stdout"],
                stderr=self.__files["stderr"],
                preexec_fn=os.setpgrp,  # noqa: PLW1509 create new process group, so signals won't be passed to child process
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

    def get_wallet_dir(self) -> Path:
        return self.__config.wallet_dir

    @classmethod
    def get_path_from_settings(cls) -> Path | None:
        return safe_settings.beekeeper.path

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
