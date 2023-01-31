from __future__ import annotations

from typing import Final

from clive.app_status import app_status
from clive.cli import STYLE_HELP
from clive.ui.internal_cli.command import Command, CommandMode

COMMANDS: Final[list[Command]] = [
    Command(
        "style",
        help_=STYLE_HELP,
        handler=None,
        mode=CommandMode.BOTH,
        children=[
            Command(
                "list",
                help_="List all available styles.",
                handler=None,
                mode=CommandMode.BOTH,
            ),
            Command(
                "update",
                help_="Set a style value.",
                handler=None,
                mode=CommandMode.BOTH,
            ),
        ],
    ),
    Command(
        "activate",
        help_="Switch to the active mode.",
        handler=app_status.activate,
        mode=CommandMode.INACTIVE,
    ),
    Command(
        "deactivate",
        help_="Switch to the inactive mode.",
        handler=app_status.deactivate,
        mode=CommandMode.ACTIVE,
    ),
]


def get_deepest_child(tokens: list[str], current_command: Command | list[Command]) -> tuple[Command | None, list[str]]:
    """
    Recursively browses `Command` tree until best match found

    Args:
        tokens (list[str]): list of tokens that needs to be processed
        current_command (Command): Command instance that is a result of processing

    Returns:
        Tuple[Optional[Command], List[str]]: if possible ot deduce, returns command and list of unmatched strings
    """
    if len(tokens) == 0:
        return (None if isinstance(current_command, list) else current_command), []

    reduced_tokens = tokens.copy()
    token = reduced_tokens.pop(0)

    if isinstance(current_command, list):
        for command in current_command:
            if command.name == token:
                return get_deepest_child(reduced_tokens, command)
    else:
        for child in current_command.children:
            if child.name == token:
                return get_deepest_child(reduced_tokens, child)
        return current_command, tokens

    return None, tokens
