from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from clive.__private.core.callback import invoke
from clive.__private.logger import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Self

    from clive.__private.ui.app import Clive


@dataclass(frozen=True)
class InternalCLICommand:
    """A command that is used internally by the CLI inside an TUI app."""

    name: str
    callback: Callable[..., None]
    help_: str = ""
    options: frozenset[str] = field(default_factory=frozenset)
    children: frozenset[Self] = field(default_factory=frozenset)


class InternalCLICommands:
    def __init__(self, app: Clive) -> None:
        self.__app = app
        self.__commands = frozenset(
            [
                InternalCLICommand("activate", options=frozenset(["active_mode_time"]), callback=self.__app.activate),
                InternalCLICommand(
                    "deactivate",
                    callback=self.__app.deactivate,
                ),
            ]
        )

    @property
    def commands(self) -> frozenset[InternalCLICommand]:
        return self.__commands

    async def handle(self, raw_text: str) -> None:
        parts = shlex.split(raw_text)

        command_name = parts[0]
        command_args = parts[1:]

        logger.info(f"Handling command: {command_name} {command_args}")

        show_help = any(h in command_args for h in ["-h", "--help", "help"])

        for command in self.__commands:
            if command_name == command.name:
                if show_help:
                    self.__app.write(self.__get_help_message(command), message_type="info")
                    return

                await invoke(command.callback, *command_args)
                self.__app.write(f"Command `{command_name}` executed successfully.", message_type="success")
                break
        else:
            self.__app.write(f"Unknown command `{command_name}`", message_type="error")

    @staticmethod
    def __get_help_message(command: InternalCLICommand) -> str:
        return f"""
    Showing help for command `{command.name}`:
    Description: {command.help_}
    Options: {", ".join(command.options)}
"""
