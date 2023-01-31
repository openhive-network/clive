from __future__ import annotations

import shlex
from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, FuzzyCompleter
from prompt_toolkit.document import Document

from clive.app_status import app_status
from clive.ui.internal_cli.command import Command, CommandMode
from clive.ui.internal_cli.commands import COMMANDS, get_deepest_child


class CliveCompleter(FuzzyCompleter):
    class __Completer(Completer):
        def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
            text = document.text_before_cursor
            text_tokenized = shlex.split(text)

            command, args = get_deepest_child(text_tokenized, COMMANDS)

            if not command:
                yield from self.__get_all_command_completions()
                return

            yield from self.__get_command_children_completions(command)

        def __get_all_command_completions(self) -> Iterable[Completion]:
            for command in COMMANDS:
                if not self.__is_command_available(command):
                    continue

                yield Completion(
                    command.name,
                    display_meta=command.help,
                )

        def __get_command_children_completions(self, command: Command) -> Iterable[Completion]:
            for child in command.children:
                if not self.__is_command_available(child):
                    continue

                yield Completion(
                    child.name,
                    display_meta=child.help,
                )

        @staticmethod
        def __is_command_available(command: Command) -> bool:
            """Return True if the current command is available in the current mode."""
            if (
                app_status.active_mode
                and command.mode == CommandMode.INACTIVE
                or not app_status.active_mode
                and command.mode == CommandMode.ACTIVE
            ):
                return False
            return True

    def __init__(self) -> None:
        super().__init__(self.__Completer())
