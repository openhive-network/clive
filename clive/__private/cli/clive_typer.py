from __future__ import annotations

import inspect
import sys
from collections.abc import Callable
from functools import partial, wraps
from typing import Any, ClassVar, NewType, TypeVar

import typer
from click import ClickException
from typer import rich_utils
from typer.main import _typer_developer_exception_attr_name
from typer.models import CommandFunctionType, Default, DeveloperExceptionConfig

from clive.__private.core._async import asyncio_run

ExceptionT = TypeVar("ExceptionT", bound=Exception)
ExitCode = NewType("ExitCode", int)
ErrorHandlingCallback = Callable[[ExceptionT], ExitCode | None]


class CliveTyper(typer.Typer):
    """
    A modified version of Typer that allows for registering error handlers and has a different defaults set.

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
    # Instead `handle_any_error` will handle it, and since it raises CLIPrettyError - it will be pretty printed.
    """

    __clive_error_handlers__: ClassVar[dict[type[Exception], ErrorHandlingCallback[Any]]] = {}
    """ClassVar since error handlers could be registered only for the main Typer instance, but not for sub-commands."""

    def __init__(
        self,
        *,
        name: str | None = Default(None),
        help: str | None = Default(None),  # noqa: A002
        chain: bool = Default(value=False),
    ) -> None:
        super().__init__(
            name=name,
            help=help,
            chain=chain,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
            no_args_is_help=True,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        try:
            return super().__call__(*args, **kwargs)
        except Exception as error:  # noqa: BLE001
            self.__handle_error(error)

    def error_handler(
        self, error: type[ExceptionT]
    ) -> Callable[[ErrorHandlingCallback[ExceptionT]], ErrorHandlingCallback[ExceptionT]]:
        def decorator(f: ErrorHandlingCallback[ExceptionT]) -> ErrorHandlingCallback[ExceptionT]:
            self.__clive_error_handlers__[error] = f
            return f

        return decorator

    def callback(self, *args: Any, **kwargs: Any) -> Callable[[CommandFunctionType], CommandFunctionType]:
        return partial(self._maybe_run_async, super().callback(*args, **kwargs))

    def command(self, *args: Any, **kwargs: Any) -> Callable[[CommandFunctionType], CommandFunctionType]:
        return partial(self._maybe_run_async, super().command(*args, **kwargs))

    @staticmethod
    def _maybe_run_async(decorator: Any, func: Any) -> Any:  # noqa: ANN401
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            return asyncio_run(func(*args, **kwargs))

        if inspect.iscoroutinefunction(func):
            return decorator(wrapper)
        return decorator(func)

    def __handle_error(self, error: ExceptionT) -> None:
        handler = self.__get_error_handler(error)

        try:
            exit_code = handler(error)
            if exit_code is None:
                # means that error was not handled by that callback, try to handle with the next one
                self.__handle_error(error)

            sys.exit(exit_code)
        except ClickException as click_exception:
            # See: `typer/core.py` -> `_main` -> `except click.ClickException as e:`
            # If ClickException was raised in the registered error handler, we need to format it like Typer does.
            rich_utils.rich_format_error(click_exception)
            sys.exit(click_exception.exit_code)
        except Exception as exception:  # noqa: BLE001
            # See: `typer/mian.py` -> `Typer.__call__` -> `except Exception as e:`
            # If any other exception was raised in the registered error handler, we need to format it like Typer does.
            setattr(
                exception,
                _typer_developer_exception_attr_name,
                DeveloperExceptionConfig(
                    pretty_exceptions_enable=self.pretty_exceptions_enable,
                    pretty_exceptions_show_locals=self.pretty_exceptions_show_locals,
                    pretty_exceptions_short=self.pretty_exceptions_short,
                ),
            )
            raise exception from None

    def __get_error_handler(self, error: ExceptionT) -> ErrorHandlingCallback[ExceptionT]:
        for type_ in type(error).mro():
            if type_ in self.__clive_error_handlers__:
                return self.__clive_error_handlers__.pop(type_)

        raise error  # reraise if no handler is available
