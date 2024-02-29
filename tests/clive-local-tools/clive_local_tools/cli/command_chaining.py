from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from .exceptions import CliveCommandError

if TYPE_CHECKING:
    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


def kwargs_to_cli_options(**kwargs: str) -> list[str]:
    options: list[str] = []
    for key, value in kwargs.items():
        option_name = key.strip("_").replace("_", "-")
        options.append(f"--{option_name}={value}")
    return options


class ChainedCommand:
    def __init__(self, command: list[str], typer: CliveTyper, runner: CliRunner, *args: str, **kwargs: str) -> None:
        self.__full_command = [*command, *args, *kwargs_to_cli_options(**kwargs)]
        self.__typer = typer
        self.__runner = runner
        self.__was_invoked = False

    def _add_command_to_chain(self, *args: str, **kwargs: str) -> None:
        self.__full_command.extend(args)
        self.__full_command.extend(kwargs_to_cli_options(**kwargs))

    def fire(self) -> Result:
        assert self.__was_invoked is False, f"Command '{self.__full_command}' was already invoked."
        self.__was_invoked = True
        tt.logger.info(f"Executing command {self.__full_command}.")
        result = self.__runner.invoke(self.__typer, self.__full_command)
        if result.exit_code != 0:
            raise CliveCommandError(self.__full_command, result.exit_code, result.stdout, result)
        return result


class UpdateAuthority(ChainedCommand):
    def add_key(self, *args: str, **kwargs: str) -> UpdateAuthority:
        self._add_command_to_chain("add-key", *args, **kwargs)
        return self

    def add_account(self, *args: str, **kwargs: str) -> UpdateAuthority:
        self._add_command_to_chain("add-account", *args, **kwargs)
        return self

    def remove_key(self, *args: str, **kwargs: str) -> UpdateAuthority:
        self._add_command_to_chain("remove-key", *args, **kwargs)
        return self

    def remove_account(self, *args: str, **kwargs: str) -> UpdateAuthority:
        self._add_command_to_chain("remove-account", *args, **kwargs)
        return self

    def modify_key(self, *args: str, **kwargs: str) -> UpdateAuthority:
        self._add_command_to_chain("modify-key", *args, **kwargs)
        return self

    def modify_account(self, *args: str, **kwargs: str) -> UpdateAuthority:
        self._add_command_to_chain("modify-account", *args, **kwargs)
        return self


class UpdateOwnerAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, *args: str, **kwargs: str) -> None:
        command = ["process", "update-owner-authority"]
        super().__init__(command, typer, runner, *args, **kwargs)


class UpdateActiveAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, *args: str, **kwargs: str) -> None:
        command = ["process", "update-active-authority"]
        super().__init__(command, typer, runner, *args, **kwargs)


class UpdatePostingAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, *args: str, **kwargs: str) -> None:
        command = ["process", "update-posting-authority"]
        super().__init__(command, typer, runner, *args, **kwargs)
