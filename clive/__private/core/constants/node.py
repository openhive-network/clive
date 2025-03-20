"""
Constants that are directly related to the HIVE blockchain behaviour and node config are stored there.

In future they will might be imported from hived through wax.
See: https://gitlab.syncad.com/hive/clive/-/issues/216
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


# HIVE config mapping (names and values correspond to the hived config.hpp, names can have unit postfix when needed)
HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS: Final[int] = 30
HIVE_PROPOSAL_MAX_IDS_NUMBER: Final[int] = 5
HIVE_MAX_RECURRENT_TRANSFER_END_DATE_DAYS: Final[int] = 730  # 2 years
HIVE_MIN_RECURRENT_TRANSFERS_RECURRENCE_HOURS: Final[int] = 24
HIVE_MAX_ACCOUNT_WITNESS_VOTES: Final[int] = 30
HIVE_GOVERNANCE_VOTE_EXPIRATION_PERIOD_DAYS: Final[int] = 365

# removal values (special values that are used to remove something in the blockchain state)
# e.g. DelegateVestingSharesOperation requires to be broadcast with amount of 0 to remove delegation
VESTS_TO_REMOVE_DELEGATION: Final[int] = 0
VESTS_TO_REMOVE_POWER_DOWN: Final[int] = 0
PERCENT_TO_REMOVE_WITHDRAW_ROUTE: Final[Decimal] = Decimal(0)
VALUE_TO_REMOVE_SCHEDULED_TRANSFER: Final[int] = 0

# claim account
HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION: Final[int] = 0

# governance
GOVERNANCE_VOTES_VALIDITY_PERIOD: Final[timedelta] = timedelta(days=HIVE_GOVERNANCE_VOTE_EXPIRATION_PERIOD_DAYS)

# scheduled transfer (also known as recurrent transfer)
SCHEDULED_TRANSFER_MAX_LIFETIME: Final[timedelta] = timedelta(days=HIVE_MAX_RECURRENT_TRANSFER_END_DATE_DAYS)
SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE: Final[timedelta] = timedelta(
    hours=HIVE_MIN_RECURRENT_TRANSFERS_RECURRENCE_HOURS
)

SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE: Final[int] = 2
SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE: Final[int] = 0

# aliased, better named
CHANGE_RECOVERY_ACCOUNT_PENDING_DAYS = HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS
DECLINE_VOTING_RIGHTS_PENDING_DAYS = HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS
MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION = HIVE_PROPOSAL_MAX_IDS_NUMBER
MAX_NUMBER_OF_WITNESSES_VOTES = HIVE_MAX_ACCOUNT_WITNESS_VOTES

# uncategorized
NULL_ACCOUNT_KEY_VALUE: Final[str] = "STM1111111111111111111111111111111114T1Anm"
PARTICIPATION_CALCULATION_SLOTS_COUNT: Final[int] = 128
