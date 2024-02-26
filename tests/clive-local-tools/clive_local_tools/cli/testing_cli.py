from __future__ import annotations

from typing import TYPE_CHECKING, Any

import test_tools as tt

from .exceptions import CliveCommandError

if TYPE_CHECKING:
    from types import TracebackType

    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


class TestingCli:
    def __init__(self, typer: CliveTyper, runner: CliRunner) -> None:
        self.__typer = typer
        self.__runner = runner

    def __getattr__(self, attr: str) -> InvocationProxy:
        new_command = attr.split("_")
        return InvocationProxy(self.__typer, self.__runner, new_command)

    def chain_commands(self) -> ChainCommandsContext:
        return ChainCommandsContext(self.__typer, self.__runner)


class ChainCommandsContext:
    def __init__(self, typer: CliveTyper, runner: CliRunner) -> None:
        self.__typer = typer
        self.__runner = runner
        self.__is_chaining_commands_in_progress = False
        self.__gathered_commands: list[str] = []
        self.__result: None | Result = None

    def get_result(self) -> Result:
        if self.__result is None:
            raise RuntimeError(
                f"There is no result stored in ChainCommandsContext, command `{self.__gathered_commands}` was not"
                " invoked"
            )
        return self.__result

    def __getattr__(self, attr: str) -> ArgsGatherer:
        if not self.__is_chaining_commands_in_progress:
            raise RuntimeError(f'You used {ChainCommandsContext.__name__}.{attr}() not in "with" statement')
        new_command = attr.split("_")
        self.__gathered_commands.extend(new_command)
        return ArgsGatherer(self.__gathered_commands)

    def __enter__(self) -> ChainCommandsContext:
        self.__is_chaining_commands_in_progress = True
        return self

    def __exit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        invocation = InvocationProxy(self.__typer, self.__runner, self.__gathered_commands)
        self.__is_chaining_commands_in_progress = False
        self.__gathered_commands = []
        self.__result = invocation()


class InvocationProxy:
    def __init__(self, typer: CliveTyper, runner: CliRunner, command: list[str]) -> None:
        self.__typer = typer
        self.__runner = runner
        self.__command = command

    def __call__(self, *args: str, **kwargs: Any) -> Result:
        args_gatherer = ArgsGatherer(self.__command)
        args_gatherer(*args, **kwargs)
        tt.logger.debug(f"executing clive command {self.__command}")

        result = self.__runner.invoke(self.__typer, self.__command)

        if result.exit_code != 0:
            raise CliveCommandError(result.stdout, result.exit_code, self.__command)
        return result


class ArgsGatherer:
    def __init__(self, list_to_extend: list[str]) -> None:
        self.__list_to_extend = list_to_extend

    def __call__(self, *args: str, **kwargs: Any) -> None:
        self.__list_to_extend.extend(args)
        args_with_values = [f"--{key}={value}" for key, value in kwargs.items()]
        self.__list_to_extend.extend(args_with_values)
