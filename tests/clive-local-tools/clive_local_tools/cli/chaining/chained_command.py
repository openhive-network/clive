from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive_local_tools.cli.command_options import kwargs_to_cli_options
from clive_local_tools.cli.exceptions import CLITestCommandError

if TYPE_CHECKING:
    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive_local_tools.cli.command_options import CliOptionT


class ChainedCommand:
    def __init__(self, typer: CliveTyper, runner: CliRunner, command: list[str], **cli_options: CliOptionT) -> None:
        self.__typer = typer
        self.__runner = runner
        self.__full_command = [*command, *kwargs_to_cli_options(**cli_options)]
        self.__was_invoked = False

    def _add_command_to_chain(self, next_command: str, **cli_options: CliOptionT) -> None:
        self.__full_command.append(next_command)
        self.__full_command.extend(kwargs_to_cli_options(**cli_options))

    def fire(self) -> Result:
        assert self.__was_invoked is False, f"Command '{self.__full_command}' was already invoked."
        self.__was_invoked = True
        tt.logger.info(f"Executing command {self.__full_command}.")
        result = self.__runner.invoke(self.__typer, self.__full_command)
        if result.exit_code != 0:
            raise CLITestCommandError(self.__full_command, result.exit_code, result.stdout, result)
        return result
