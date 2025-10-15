from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

import typer

if TYPE_CHECKING:
    from typer.models import ArgumentInfo, OptionInfo


def argument_to_option(argument: typer.models.ArgumentInfo, *param_decls: str) -> Any:  # noqa: ANN401
    """
    Transform a Typer Argument into an Option.

    Args:
        argument: The typer.Argument(...) object to transform.
        *param_decls: Optional names for option.

    Returns:
        typer.Option(...) equivalent to the input Argument.
    """
    for name in param_decls:
        assert name.startswith("-"), "Option name must start with '-'"
    # Reuse settings from the original Argument
    return typer.Option(
        argument.default,
        *param_decls,
        callback=argument.callback,
        metavar=argument.metavar,
        expose_value=argument.expose_value,
        is_eager=argument.is_eager,
        envvar=argument.envvar,
        shell_complete=argument.shell_complete,
        autocompletion=argument.autocompletion,
        default_factory=argument.default_factory,
        # Custom type
        parser=argument.parser,
        # Option
        show_default=argument.show_default,
        help=argument.help,
        hidden=argument.hidden,
        show_choices=argument.show_choices,
        show_envvar=argument.show_envvar,
        # Choice
        case_sensitive=argument.case_sensitive,
        # Numbers
        min=argument.min,
        max=argument.max,
        clamp=argument.clamp,
        # DateTime
        formats=argument.formats,
        # File
        mode=argument.mode,
        encoding=argument.encoding,
        errors=argument.errors,
        lazy=argument.lazy,
        atomic=argument.atomic,
        # Path
        exists=argument.exists,
        file_okay=argument.file_okay,
        dir_okay=argument.dir_okay,
        writable=argument.writable,
        readable=argument.readable,
        resolve_path=argument.resolve_path,
        allow_dash=argument.allow_dash,
        path_type=argument.path_type,
        # Rich settings
        rich_help_panel=argument.rich_help_panel,
    )


def modified_param(source: OptionInfo | ArgumentInfo, **kwargs: Any) -> Any:  # noqa: ANN401
    """
    Create option/argument based on another option/argument, but with some attributes modified.

    Args:
        source: The option/argument to modify.
        **kwargs: The attributes to modify.

    Raises:
        ValueError: If an unknown attribute is specified in kwargs.

    Returns:
        A modified option/argument based on the source with the specified attributes changed.
    """
    destination = deepcopy(source)
    for key, value in kwargs.items():
        if not hasattr(destination, key):
            raise ValueError(f"Unknown option attribute: {key}\navailable attributes: {list(source.__dict__)}")
        setattr(destination, key, value)
    return destination
