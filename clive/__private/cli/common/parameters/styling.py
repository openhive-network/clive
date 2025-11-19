from __future__ import annotations

from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION


def stylized_help(
    help_message: str,
    *,
    default: str | None = None,
    is_working_account_default: bool = False,
    required_as_arg_or_option: bool = False,
) -> str:
    assert not is_working_account_default or default is None, (
        "Only one of parameters: `is_working_account_default` or `default` can be given."
    )

    if is_working_account_default:
        help_message = _append_default(help_message, "working account of profile")

    if default is not None:
        help_message = _append_default(help_message, default)

    if required_as_arg_or_option:
        help_message = _append_required_as_arg_or_option(help_message)
    return help_message


def _append_default(help_message: str, default: str) -> str:
    from rich.text import Text  # noqa: PLC0415
    from typer.rich_utils import DEFAULT_STRING, STYLE_OPTION_DEFAULT  # noqa: PLC0415

    postfix = Text(DEFAULT_STRING.format(default), style=STYLE_OPTION_DEFAULT)
    return f"{help_message} {postfix.markup}"


def _append_required_as_arg_or_option(help_message: str) -> str:
    from rich.text import Text  # noqa: PLC0415
    from typer.rich_utils import STYLE_REQUIRED_LONG  # noqa: PLC0415

    postfix = Text(REQUIRED_AS_ARG_OR_OPTION, style=STYLE_REQUIRED_LONG)
    return f"{help_message} {postfix.markup}"
