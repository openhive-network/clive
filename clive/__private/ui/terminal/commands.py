from __future__ import annotations

import inspect
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, ClassVar

import typer.models

from clive.__private import cli
from clive.__private.cli.common import get_function_parameters
from clive.__private.core.callback import invoke
from clive.__private.core.clive_import import get_clive
from clive.__private.core.perform_actions_on_transaction import perform_actions_on_transaction
from clive.__private.logger import logger
from schemas.__private.operations import TransferOperation
from test_tools import PublicKey

if TYPE_CHECKING:
    from typing_extensions import Self

    from clive.__private.ui.app import Clive


@dataclass
class ICLIOption:
    name: str
    help_: str
    type_: type
    default: Any

    @classmethod
    def create_from_parameter(cls, parameter: inspect.Parameter) -> Self:
        option_info: typer.models.OptionInfo = parameter.default

        return cls(
            name=parameter.name,
            help_=option_info.help,
            type_=parameter.annotation,
            default=option_info.default,
        )


@dataclass
class ICLICommand(ABC):
    """A command that is used internally by the CLI inside an TUI app."""

    name: str
    help_: str = ""
    options: list[ICLIOption] = field(default_factory=list)
    children: list[Self] = field(default_factory=list)
    _app: ClassVar[Clive] = get_clive().app_instance()

    @abstractmethod
    def execute(self, *args: str) -> None:
        """Should implement how to execute the command."""

    @classmethod
    def create(
        cls, name: str, parameters: list[inspect.Parameter], help_: str = "", children: list[Self] | None = None
    ) -> Self:
        return cls(
            name=name,
            help_=help_,
            options=[ICLIOption.create_from_parameter(p) for p in parameters],
            children=children or [],
        )


class Transfer(ICLICommand):
    def execute(self) -> None:
        perform_actions_on_transaction(
            TransferOperation(from_=from_, to=to, amount=Asset.from_legacy(amount.upper()), memo=memo),
            beekeeper=self._app.world.beekeeper,
            node=self._app.world.node,
            sign_key=PublicKey(common.sign) if common.sign else None,
            save_file_path=Path(common.save_file) if common.save_file else None,
            broadcast=self._app.broadcast,
            chain_id=self._app.world.node.chain_id,
        )


COMMANDS: Final[list[ICLICommand]] = [
    Transfer.create(
        name="transfer",
        parameters=get_function_parameters(cli.transfer._main),
    )

]


@dataclass
class InternalCLICommands:
    _commands = frozenset(COMMANDS)
    _app: Clive = get_clive().app_instance()

    async def handle(self, raw_text: str) -> None:
        parts = shlex.split(raw_text)

        command_name = parts[0]
        command_args = parts[1:]

        logger.info(f"Handling command: {command_name} {command_args}")

        show_help = any(h in command_args for h in ["-h", "--help", "help"])

        for command in self._commands:
            if command_name == command.name:
                if show_help:
                    self.__show_help(command)
                    return

                await invoke(command.callback, *command_args)
                self._app.write(f"Command `{command_name}` executed successfully.", message_type="success")
                break
        else:
            self._app.write(f"Unknown command `{command_name}`", message_type="error")

    def __show_help(self, command: ICLICommand) -> None:
        self._app.write(self.__get_help_message(command), message_type="info")

    @staticmethod
    def __get_help_message(command: ICLICommand) -> str:
        message = f"Help for command `{command.name}`:\n"

        if command.help_:
            message += f"Description: {command.help_}\n"

        if command.options:
            options = ",\n".join(str(option) for option in command.options)
            message += f"Options:\n{options}"
        return message
