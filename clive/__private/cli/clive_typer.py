import contextlib
import sys
from collections.abc import Callable
from dataclasses import fields
from functools import wraps
from inspect import Parameter, isawaitable, signature
from typing import Any, ClassVar, NewType, Optional, TypeVar

import typer
from click import ClickException
from typer import rich_utils
from typer.main import _typer_developer_exception_attr_name
from typer.models import CommandFunctionType, Default, DeveloperExceptionConfig

from clive.__private.cli.common.common_options_base import CommonOptionInstanceNotAvailableError, CommonOptionsBase
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
        name: Optional[str] = Default(None),
        help: Optional[str] = Default(None),  # noqa: A002
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

    def __common_decorator(
        self,
        fun: Callable[..., Any],
        common_options: list[type[CommonOptionsBase]] | None = None,
        **kwargs: Any,
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        common_options = common_options or []

        def decorator(f: CommandFunctionType) -> CommandFunctionType:
            @wraps(f)
            def wrapper(*args: Any, **_kwargs: Any) -> Any:  # noqa: ANN401
                if len(args) > 0:
                    raise RuntimeError("Positional arguments are not supported")

                for common_option in common_options:
                    _kwargs = self.__patch_wrapper_kwargs(common_option, **_kwargs)

                result = f(*args, **_kwargs)

                if isawaitable(result):
                    asyncio_run(result)

            for common_option in common_options:
                self.__patch_command_sig(wrapper, common_option)

            return fun(**kwargs)(wrapper)  # type: ignore[no-any-return]

        return decorator

    def command(  # type: ignore[override]
        self,
        name: Optional[str] = None,
        common_options: list[type[CommonOptionsBase]] | None = None,
        *,
        help: Optional[str] = None,  # noqa: A002
        epilog: Optional[str] = None,
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        return self.__common_decorator(
            super().command, name=name, common_options=common_options, help=help, epilog=epilog
        )

    def callback(  # type: ignore[override]
        self,
        name: Optional[str] = Default(None),
        common_options: list[type[CommonOptionsBase]] | None = None,
        *,
        help: Optional[str] = Default(None),  # noqa: A002
        invoke_without_command: bool = Default(value=False),
        result_callback: Optional[Callable[..., Any]] = Default(None),
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        return self.__common_decorator(
            super().callback,
            name=name,
            common_options=common_options,
            help=help,
            invoke_without_command=invoke_without_command,
            result_callback=result_callback,
        )

    def __handle_error(self, error: ExceptionT) -> None:
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
        except Exception as error:  # noqa: BLE001
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

    def __get_error_handler(self, error: ExceptionT) -> ErrorHandlingCallback[ExceptionT]:
        for type_ in type(error).mro():
            if type_ in self.__clive_error_handlers__:
                return self.__clive_error_handlers__.pop(type_)

        raise error  # reraise if no handler is available

    @staticmethod
    def __patch_wrapper_kwargs(common_option: type[CommonOptionsBase], **kwargs: Any) -> dict[str, Any]:
        if (ctx := kwargs.get("ctx")) is None:
            raise RuntimeError("Context should be provided")

        common_opts_params: dict[str, Any] = {}

        with contextlib.suppress(CommonOptionInstanceNotAvailableError):
            common_opts_params.update(common_option.get_instance().as_dict())

        for field in fields(common_option):
            if field.metadata.get("ignore", False):
                continue

            value = kwargs.pop(field.name)

            if value == field.default:
                continue

            common_opts_params[field.name] = value

        common_option(**common_opts_params)
        setattr(ctx, common_option.get_name(), common_opts_params)

        return {"ctx": ctx, **kwargs}

    @staticmethod
    def __patch_command_sig(wrapper: Any, common_option: type[CommonOptionsBase]) -> None:  # noqa: ANN401
        sig = signature(wrapper)
        new_parameters = sig.parameters.copy()

        common_option_fields = fields(common_option)

        for field in common_option_fields:
            if field.metadata.get("ignore", False):
                continue
            new_parameters[field.name] = Parameter(
                name=field.name,
                kind=Parameter.KEYWORD_ONLY,
                default=field.default,
                annotation=field.type,
            )
        for kwarg in sig.parameters.values():
            if kwarg.kind == Parameter.KEYWORD_ONLY and kwarg.name != "ctx" and kwarg.name not in new_parameters:
                new_parameters[kwarg.name] = kwarg.replace(default=kwarg.default)

        new_sig = sig.replace(parameters=tuple(new_parameters.values()))
        wrapper.__signature__ = new_sig
