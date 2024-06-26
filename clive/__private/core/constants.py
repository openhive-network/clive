from __future__ import annotations

from decimal import Decimal
from math import floor, log10
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION: Final[int] = 5
HIVE_PERCENT_PRECISION: Final[int] = 100
HIVE_PERCENT_PRECISION_DOT_PLACES: Final[int] = floor(log10(HIVE_PERCENT_PRECISION))

VESTS_TO_HIVE_RATIO_PRECISION: Final[int] = 1000
VESTS_TO_HIVE_RATIO_PRECISION_DOT_PLACES: Final[int] = floor(log10(VESTS_TO_HIVE_RATIO_PRECISION))

NULL_ACCOUNT_KEY_VALUE: Final[str] = "STM1111111111111111111111111111111114T1Anm"
PARTICIPATION_CALCULATION_SLOTS_COUNT: Final[int] = 128

VESTS_REMOVE_DELEGATION_AMOUNT: Final[int] = 0
VESTS_REMOVE_POWER_DOWN_AMOUNT: Final[int] = 0
PERCENT_REMOVE_WITHDRAW_ROUTE_AMOUNT: Final[Decimal] = Decimal(0)
HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION: Final[int] = 0

SCHEDULED_TRANSFER_MINIMUM_FREQUENCY_VALUE: Final[int] = 24
SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE: Final[int] = 2
SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE: Final[int] = 0
SCHEDULED_TRANSFER_TWO_YEARS_MAX_LIFETIME_DURATION_IN_HOURS: Final[int] = 2 * 365 * 24

TERMINAL_HEIGHT: Final[int] = 24
TERMINAL_WIDTH: Final[int] = 132

HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS: Final[int] = 30
DECLINE_VOTING_RIGHTS_PENDING_DAYS = HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS
CHANGE_RECOVERY_ACCOUNT_PENDING_DAYS = HIVE_OWNER_AUTH_RECOVERY_PERIOD_DAYS
