from __future__ import annotations

from typing import ClassVar

from clive.__private.validators.set_watched_account_validator import SetWatchedAccountValidator


class SetWorkingAccountValidator(SetWatchedAccountValidator):
    ACCOUNT_ALREADY_WORKING_FAILURE: ClassVar[str] = "This account is already a working account."
    ACCOUNT_ALREADY_WATCHED_FAILURE: ClassVar[str] = "You cannot set account as working while its already watched."
