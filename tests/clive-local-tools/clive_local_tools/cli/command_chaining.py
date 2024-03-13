from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from .exceptions import CliveCommandError

if TYPE_CHECKING:
    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive_local_tools.cli.command_options import KwargsType


def kwargs_to_cli_options(**kwargs: KwargsType) -> list[str]:
    options: list[str] = []
    for key, value in kwargs.items():
        option_name = key.strip("_").replace("_", "-")
        if value is True:
            options.append(f"--{option_name}")
        elif value is False:
            options.append(f"--no-{option_name}")
        elif value is not None:
            options.append(f"--{option_name}={value}")
    return options


class ChainedCommand:
    def __init__(self, command: list[str], typer: CliveTyper, runner: CliRunner, **kwargs: KwargsType) -> None:
        self.__full_command = [*command, *kwargs_to_cli_options(**kwargs)]
        self.__typer = typer
        self.__runner = runner
        self.__was_invoked = False

    def _add_command_to_chain(self, **kwargs: KwargsType) -> None:
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
    def add_key(self, **kwargs: KwargsType) -> UpdateAuthority:
        self._add_command_to_chain("add-key", **kwargs)
        return self

    def add_account(self, **kwargs: KwargsType) -> UpdateAuthority:
        self._add_command_to_chain("add-account", **kwargs)
        return self

    def remove_key(self, **kwargs: KwargsType) -> UpdateAuthority:
        self._add_command_to_chain("remove-key", **kwargs)
        return self

    def remove_account(self, **kwargs: KwargsType) -> UpdateAuthority:
        self._add_command_to_chain("remove-account", **kwargs)
        return self

    def modify_key(self, **kwargs: KwargsType) -> UpdateAuthority:
        self._add_command_to_chain("modify-key", **kwargs)
        return self

    def modify_account(self, **kwargs: KwargsType) -> UpdateAuthority:
        self._add_command_to_chain("modify-account", **kwargs)
        return self


class UpdateOwnerAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, **kwargs: KwargsType) -> None:
        command = ["process", "update-owner-authority"]
        super().__init__(command, typer, runner, **kwargs)


class UpdateActiveAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, **kwargs: KwargsType) -> None:
        command = ["process", "update-active-authority"]
        super().__init__(command, typer, runner, **kwargs)


class UpdatePostingAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, **kwargs: KwargsType) -> None:
        command = ["process", "update-posting-authority"]
        super().__init__(command, typer, runner, **kwargs)
