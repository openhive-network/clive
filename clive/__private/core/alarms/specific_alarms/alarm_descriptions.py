from __future__ import annotations

from typing import Final

GOVERNANCE_COMMON_ALARM_DESCRIPTION: Final[str] = (
    "Governance votes are votes on proposals and witnesses.\n"
    "You can vote for 30 witnesses and an unlimited number of proposals.\n"  # TODO: change 30 to const after merging: https://gitlab.syncad.com/hive/clive/-/merge_requests/387
    "The governance votes are valid one year."
)
GOVERNANCE_VOTING_EXPIRATION_ALARM_DESCRIPTION: Final[str] = (
    f"{GOVERNANCE_COMMON_ALARM_DESCRIPTION}\n"
    "Alarm applies to the expiration of the last vote (no matter whether it is a vote for a witness or a proposal)."
)
DECLINING_VOTING_RIGHTS_IN_PROGRESS_ALARM_DESCRIPTION: Final[str] = (
    "The decline voting rights operation is in progress.\n"
    "After effective date the operation is irreversible.\n"
    "The operation prevents voting on witnesses, proposals, posts and comments."
)
RECOVERY_ACCOUNT_WARNING_LISTED_ALARM_DESCRIPTION: Final[str] = (
    "It is important to keep the recovery account up to date.\n"
    "If you lose your owner key, you will not be able to recover your account."
)
CHANGING_RECOVERY_ACCOUNT_IN_PROGRESS_ALARM_DESCRIPTION: Final[str] = (
    "`change_recovery_account_operation` allows a user to update their recovery account.\n"
    "Only a recovery account may create a request account recovery in case of compromised the owner authority."
)
