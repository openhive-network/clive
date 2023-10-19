import sys
from collections.abc import Callable
from typing import Any, ClassVar, NewType

import typer
from click import ClickException
from typer import rich_utils
from typer.main import _typer_developer_exception_attr_name
from typer.models import DeveloperExceptionConfig

ExitCode = NewType("ExitCode", int)
ErrorHandlingCallback = Callable[[Exception], ExitCode | None]


class CliveTyper(typer.Typer):
    """
    A modified version of Typer that allows for registering error handlers.

    Such a handlers could be only registered for the main Typer instance, but not for sub-commands. That's because
    Typer.__call__ is not called for each sub-commands, but only for the main Typer instance.

    Example:
    -------
    >>> raise TypeError("Some error")

    @typer_instance.error_handler(SomeError)
    def may_handle_some_error(error: SomeError) -> int | None:
        if "Other error" in str(error):
            typer.echo("Some error occurred")
            return 1
        return None

    @typer_instance.error_handler(Exception)
    def handle_any_error(error: Exception) -> None:
        raise CLIError(str(error), 1)

    # `may_handle_some_error` will ignore the error, because of the `if` condition.
    # Instead `handle_any_error` will handle it, and since it raises CLIError - it will be pretty printed.
    """

    __clive_error_handlers__: ClassVar[dict[type[Exception], ErrorHandlingCallback]] = {}
    """ClassVar since error handlers could be registered only for the main Typer instance, but not for sub-commands."""

    def error_handler(self, error: type[Exception]) -> Callable[[ErrorHandlingCallback], ErrorHandlingCallback]:
        def decorator(f: ErrorHandlingCallback) -> ErrorHandlingCallback:
            self.__clive_error_handlers__[error] = f
            return f

        return decorator

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return super().__call__(*args, **kwargs)
        except Exception as error:  # noqa: BLE001
            self.__handle_error(error)

    def __handle_error(self, error: Exception) -> None:
        handler = self.__get_error_handler(error)

        try:
            exit_code = handler(error)
            if exit_code is None:
                # means that error was not handled by that callback, try to handle with the next one
                self.__handle_error(error)

            sys.exit(exit_code)
        except ClickException as error:
            # See: `typer/core.py` -> `_main` -> `except click.ClickException as e:`
            # If ClickException was raised in the registered error handler, we need to format it like Typer does.
            rich_utils.rich_format_error(error)
            sys.exit(error.exit_code)
        except Exception as error:
            # See: `typer/mian.py` -> `Typer.__call__` -> `except Exception as e:`
            # If any other exception was raised in the registered error handler, we need to format it like Typer does.
            setattr(
                error,
                _typer_developer_exception_attr_name,
                DeveloperExceptionConfig(
                    pretty_exceptions_enable=self.pretty_exceptions_enable,
                    pretty_exceptions_show_locals=self.pretty_exceptions_show_locals,
                    pretty_exceptions_short=self.pretty_exceptions_short,
                ),
            )
            raise error from None

    def __get_error_handler(self, error: Exception) -> ErrorHandlingCallback:
        for type_ in type(error).mro():
            if type_ in self.__clive_error_handlers__:
                return self.__clive_error_handlers__.pop(type_)

        raise error  # reraise if no handler is available
