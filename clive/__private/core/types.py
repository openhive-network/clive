from __future__ import annotations

from typing import Literal

MigrationStatus = Literal["migrated", "already_newest"]

NotifyLevel = Literal["info", "warning", "error"]

OrderDirections = Literal["ascending", "descending"]

AlreadySignedMode = Literal["strict", "override", "multisign"]

ProposalOrders = Literal[
    "by_total_votes_with_voted_first", "by_total_votes", "by_start_date", "by_end_date", "by_creator"
]
ProposalStatuses = Literal["all", "active", "inactive", "votable", "expired"]

WitnessesSearchModes = Literal["search_by_pattern", "search_top_with_voted_first"]

AuthorityLevelRegular = Literal["owner", "active", "posting"]
AuthorityLevelMemo = Literal["memo"]
AuthorityLevel = Literal["owner", "active", "posting", "memo"]
"""A combination of regular and memo levels."""
