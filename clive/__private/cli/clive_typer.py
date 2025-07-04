from __future__ import annotations

import inspect
import sys
from collections.abc import Callable
from functools import partial, wraps
from typing import Any, ClassVar

import typer
from click import ClickException
from typer import rich_utils
from typer.main import _typer_developer_exception_attr_name
from typer.models import CommandFunctionType, Default, DeveloperExceptionConfig

from clive.__private.core._async import asyncio_run

type ExitCode = int
type ErrorHandlingCallback[T: Exception] = Callable[[T], ExitCode | None]


class CliveTyper(typer.Typer):
    """
    A modified version of Typer that allows for registering error handlers and has a different defaults set.

    Such a handlers could be only registered for the main Typer instance, but not for sub-commands. That's because
    Typer.__call__ is not called for each sub-commands, but only for the main Typer instance.

    Examples:
        >>> raise TypeError("Some error")

        >>> @typer_instance.error_handler(SomeError)
        >>> def may_handle_some_error(error: SomeError) -> int | None:
            >>> if "Other error" in str(error):
                >>> typer.echo("Some error occurred")
                >>> return 1
            >>> return None

        >>> @typer_instance.error_handler(Exception)
        >>> def handle_any_error(error: Exception) -> None:
            >>> raise CLIError(str(error), 1)

        >>> # `may_handle_some_error` will ignore the error, because of the `if` condition.
        >>> # Instead `handle_any_error` will handle it, and since it raises CLIPrettyError - it will be pretty printed.
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
        """
        Initialize the CliveTyper instance with the given name, help text, and chain option.

        Args:
            name: The name of the Typer application.
            help: The help text for the Typer application.
            chain: Whether to allow chaining commands (default is False).

        Returns:
            None
        """
        super().__init__(
            name=name,
            help=help,
            chain=chain,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
            no_args_is_help=True,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """
        Call the Typer instance, handling errors with registered error handlers.

        Args:
            *args: Positional arguments to pass to the Typer instance.
            **kwargs: Keyword arguments to pass to the Typer instance.

        Raises:
            Exception: If an error occurs and no handler is registered for it.

        Returns:
            Any: The result of the Typer instance call.
        """
        try:
            return super().__call__(*args, **kwargs)
        except Exception as error:  # noqa: BLE001
            self.__handle_error(error)

    def error_handler[T: Exception](
        self, error: type[T]
    ) -> Callable[[ErrorHandlingCallback[T]], ErrorHandlingCallback[T]]:
        """
        Register an error handler for a specific exception type.

        Args:
            error: The type of exception to handle.

        Returns:
            Callable, ErrorHandlingCallback: A decorator that registers the error handling callback.
        """

        def decorator(f: ErrorHandlingCallback[T]) -> ErrorHandlingCallback[T]:
            """
            Register an error handling callback for a specific exception type.

            Args:
                f: The error handling callback function to register.

            Returns:
                ErrorHandlingCallback: The registered error handling callback function.
            """
            self.__clive_error_handlers__[error] = f
            return f

        return decorator

    def callback(self, *args: Any, **kwargs: Any) -> Callable[[CommandFunctionType], CommandFunctionType]:
        """
        Register a callback function that will be executed when the command is called.

        Args:
            *args: Positional arguments to pass to the callback.
            **kwargs: Keyword arguments to pass to the callback.

        Returns:
            Callable, CommandFunctionType: A decorator that registers the callback function.
        """
        return partial(self._maybe_run_async, super().callback(*args, **kwargs))

    def command(self, *args: Any, **kwargs: Any) -> Callable[[CommandFunctionType], CommandFunctionType]:
        """
        Register a command function that will be executed when the command is called.

        Args:
            *args: Positional arguments to pass to the command.
            **kwargs: Keyword arguments to pass to the command.

        Returns:
            Callable, CommandFunctionType: A decorator that registers the command function.
        """
        return partial(self._maybe_run_async, super().command(*args, **kwargs))

    @staticmethod
    def _maybe_run_async(decorator: Any, func: Any) -> Any:  # noqa: ANN401
        """
        Run the function asynchronously if it is a coroutine function.

        Args:
            decorator: The decorator to apply to the function.
            func: The function to potentially run asynchronously.

        Returns:
            Any: The decorated function, which will run asynchronously if it is a coroutine function.
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            """
            Wrap the decorated function to run asynchronously if it is a coroutine function.

            Args:
                *args: Positional arguments to pass to the function.
                **kwargs: Keyword arguments to pass to the function.

            Returns:
                Any: The result of the function call, run asynchronously if it is a coroutine function.
            """
            return asyncio_run(func(*args, **kwargs))

        if inspect.iscoroutinefunction(func):
            return decorator(wrapper)
        return decorator(func)

    def __handle_error(self, error: Exception) -> None:
        """
        Handle an error by finding the appropriate error handler and executing it.

        Args:
            error: The exception to handle.

        Raises:
            ClickException: If the error handler raises a ClickException.
            Exception: If any other exception is raised in the error handler.

        Returns:
            None: The function does not return anything, but it exits the program with the appropriate exit code.
        """
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

    def __get_error_handler[T: Exception](self, error: T) -> ErrorHandlingCallback[T]:
        """
        Get the error handler for the given error type.

        Args:
            error: The exception for which to find the handler.

        Raises:
            error: If no handler is found for the error type, the original error is raised.

        Returns:
            ErrorHandlingCallback: The error handling callback function for the given error type.
        """
        for type_ in type(error).mro():
            if type_ in self.__clive_error_handlers__:
                return self.__clive_error_handlers__.pop(type_)

        raise error  # reraise if no handler is available
