from __future__ import annotations

from typing import Final, get_args

from clive.__private.core.types import (
    AlreadySignedMode,
    OrderDirections,
    ProposalOrders,
    ProposalStatuses,
    WitnessesSearchModes,
)

ORDER_DIRECTIONS: Final[tuple[OrderDirections, ...]] = get_args(OrderDirections)
ORDER_DIRECTION_DEFAULT: Final[OrderDirections] = "descending"

PROPOSAL_ORDERS: Final[tuple[ProposalOrders, ...]] = get_args(ProposalOrders)
PROPOSAL_ORDER_DEFAULT: Final[ProposalOrders] = "by_total_votes_with_voted_first"

PROPOSAL_STATUSES: Final[tuple[ProposalStatuses, ...]] = get_args(ProposalStatuses)
PROPOSAL_STATUS_DEFAULT: Final[ProposalStatuses] = "votable"

WITNESSES_SEARCH_MODE_DEFAULT: Final[WitnessesSearchModes] = "search_top_with_voted_first"
WITNESSES_SEARCH_BY_PATTERN_LIMIT_DEFAULT: Final[int] = 50

ALREADY_SIGNED_MODES: Final[tuple[AlreadySignedMode, ...]] = get_args(AlreadySignedMode)
ALREADY_SIGNED_MODE_DEFAULT: Final[AlreadySignedMode] = "strict"
