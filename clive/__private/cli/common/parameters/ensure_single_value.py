from functools import partial
from typing import Literal, TypeVar, overload

from clive.__private.cli.exceptions import CLIPrettyError

ExpectedT = TypeVar("ExpectedT")


@overload
def ensure_single_value(
    positional: ExpectedT | None,
    option: ExpectedT | None,
    option_name: str,
    *,
    allow_none: Literal[False] = False,
) -> ExpectedT: ...


@overload
def ensure_single_value(
    positional: ExpectedT | None,
    option: ExpectedT | None,
    option_name: str,
    *,
    allow_none: Literal[True],
) -> ExpectedT | None: ...


def ensure_single_value(
    positional: ExpectedT | None,
    option: ExpectedT | None,
    option_name: str,
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
        allow_none: When argument and option is not required.
    """
    if allow_none and positional is None and option is None:
        return None

    value = option if option is not None else positional
    if value is None:
        raise CLIPrettyError(f"Missing required argument or option: '[{option_name.upper()}]' or '--{option_name}'.")
    return value


ensure_single_value_account_name = partial(ensure_single_value, option_name="account-name")  # type: ignore[var-annotated]

ensure_single_value_profile_name = partial(ensure_single_value, option_name="profile-name")  # type: ignore[var-annotated]
