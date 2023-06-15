"""File with available operations and matching buttons"""
from __future__ import annotations

from typing import Any, Final

from clive.__private.ui.operations.account_witness_vote.account_witnes_vote import AccountWitnessVote
from clive.__private.ui.operations.covnert.covnert import Convert
from clive.__private.ui.operations.transfer_to_account.transfer_to_account import TransferToAccount
from clive.__private.ui.operations.transfer_to_savings.transfer_to_savings import TransferToSavings
from clive.__private.ui.operations.vote.vote import Vote

OPERATIONS_AND_BUTTONS: Final[dict[str, Any]] = {
    "account-transfer-button": TransferToAccount,
    "savings-transfer-button": TransferToSavings,
    "vote-button": Vote,
    "convert-button": Convert,
    "account-witness-vote-button": AccountWitnessVote,
}
