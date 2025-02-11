from __future__ import annotations

from typing import Final

PERFORM_WORKING_ACCOUNT_LOAD: Final[str] = "PERFORM_WORKING_ACCOUNT_LOAD"

REQUIRED_AS_ARG_OR_OPTION: Final[str] = "required as argument or option"

LOOK_INTO_ARGUMENT_OPTION_HELP: Final[str] = (
    "For more help look into argument description. This option takes precedence over positional argument."
)

OPERATION_COMMON_OPTIONS_PANEL_TITLE: Final[str] = "Operation common options"

UNLOCK_CREATE_PROFILE_HELP: Final[str] = (
    "There are no profiles to unlock.\n"
    "To create a new profile, please enter the following command:\n"
    "`clive configure profile add --profile-name PROFILE_NAME` and pass password to the standard input."
)
UNLOCK_CREATE_PROFILE_SELECT: Final[str] = "create a new profile"

PAGE_SIZE_OPTION_MINIMAL_VALUE: Final[int] = 1
PAGE_NUMBER_OPTION_MINIMAL_VALUE: Final[int] = 0
