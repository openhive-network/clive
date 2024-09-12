from functools import partial
from typing import Literal, TypeVar, overload

import typer
from click import ClickException

ExpectedT = TypeVar("ExpectedT")


@overload
def ensure_single_value(
    positional: ExpectedT | None,
    option: ExpectedT | None,
    option_name: str,
    expected_type: type[ExpectedT] = str,  # type: ignore[assignment]
    *,
    allow_none: Literal[False] = False,
) -> ExpectedT: ...


@overload
def ensure_single_value(
    positional: ExpectedT | None,
    option: ExpectedT | None,
    option_name: str,
    expected_type: type[ExpectedT] = str,  # type: ignore[assignment]
    *,
    allow_none: Literal[True],
) -> ExpectedT | None: ...


def ensure_single_value(
    positional: ExpectedT | None,
    option: ExpectedT | None,
    option_name: str,
    expected_type: type[ExpectedT] = str,  # type: ignore[assignment]
    *,
    allow_none: bool = False,
) -> ExpectedT | None:
    """
    Ensure that only one value is retrieved.

    Option takes precedence over positional argument

    Args:
    ----
        positional: The positional argument value.
        option: The option argument value.
        option_name: The name of the option.
        expected_type: The expected type of the value.
        allow_none: When argument and option is not required.
    """
    if allow_none and positional is None and option is None:
        return None

    value = option if option is not None else positional
    param_hint = f"'[{option_name.upper()}]' or '--{option_name}'"
    if value is None:
        raise ClickException(f"Missing required argument or option: {param_hint}.")
    if not isinstance(value, expected_type):
        raise typer.BadParameter(f"Expected {expected_type} type, but got: {type(value)}", param_hint=param_hint)
    return value


ensure_single_value_account_name = partial(ensure_single_value, option_name="account-name")

ensure_single_value_profile_name = partial(ensure_single_value, option_name="profile-name")
