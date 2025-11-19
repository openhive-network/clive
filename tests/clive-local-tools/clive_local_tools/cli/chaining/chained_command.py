from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive_local_tools.cli.command_options import build_cli_options, stringify_parameter_value
from clive_local_tools.cli.exceptions import CLITestCommandError

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive_local_tools.cli.command_options import CLIArgumentValue, CLIOptionValue


class ChainedCommand:
    def __init__(
        self,
        typer: CliveTyper,
        runner: CliRunner,
        command: list[str],
        *,
        cli_positional_args: Iterable[CLIArgumentValue] | None = None,
        cli_named_options: Mapping[str, CLIOptionValue] | None = None,
    ) -> None:
        self.__typer = typer
        self.__runner = runner
        positional = (
            [stringify_parameter_value(arg) for arg in cli_positional_args] if cli_positional_args is not None else []
        )
        named = build_cli_options(cli_named_options) if cli_named_options is not None else []
        self.__full_command = [*command, *positional, *named]
        self.__was_invoked = False

    def _add_command_to_chain(
        self,
        next_command: str,
        *,
        cli_positional_args: Iterable[CLIArgumentValue] | None = None,
        cli_named_options: Mapping[str, CLIOptionValue] | None = None,
    ) -> None:
        self.__full_command.append(next_command)

        positional = (
            [stringify_parameter_value(arg) for arg in cli_positional_args] if cli_positional_args is not None else []
        )
        named = build_cli_options(cli_named_options) if cli_named_options is not None else []
        self.__full_command.extend(positional)
        self.__full_command.extend(named)

    def fire(self) -> Result:
        assert self.__was_invoked is False, f"Command '{self.__full_command}' was already invoked."
        self.__was_invoked = True
        tt.logger.info(f"Executing command {self.__full_command}.")
        result = self.__runner.invoke(self.__typer, self.__full_command)
        if result.exit_code != 0:
            raise CLITestCommandError(self.__full_command, result.exit_code, result.stdout, result)
        return result
