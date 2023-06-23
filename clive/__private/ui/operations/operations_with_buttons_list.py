"""File with available operations and matching buttons"""
from __future__ import annotations

from typing import Any, Final

from clive.__private.ui.operations.account_witness_proxy.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.operations.account_witness_vote.account_witnes_vote import AccountWitnessVote
from clive.__private.ui.operations.cancel_transfer_from_savings.cancel_transfer_from_savings import (
    CancelTransferFromSavings,
)
from clive.__private.ui.operations.change_recovery_account.change_recovery_account import ChangeRecoveryAccount
from clive.__private.ui.operations.claim_account.claim_account import ClaimAccount
from clive.__private.ui.operations.covnert.covnert import Convert
from clive.__private.ui.operations.remove_proposal.remove_proposal import RemoveProposal
from clive.__private.ui.operations.set_reset_account.set_reset_account import SetResetAccount
from clive.__private.ui.operations.set_withdraw_vesting_route.set_withdraw_vesting_route import SetWithdrawVestingRoute
from clive.__private.ui.operations.transfer_from_savings.transfer_from_savings import TransferFromSavings
from clive.__private.ui.operations.transfer_to_account.transfer_to_account import TransferToAccount
from clive.__private.ui.operations.transfer_to_savings.transfer_to_savings import TransferToSavings
from clive.__private.ui.operations.transfer_to_vesting.transfer_to_vesting import TransferToVesting
from clive.__private.ui.operations.update_proposal.update_proposal import UpdateProposal
from clive.__private.ui.operations.update_proposal_votes.update_proposal_votes import UpdateProposalVotes
from clive.__private.ui.operations.vote.vote import Vote
from clive.__private.ui.operations.withdraw_vesting.withdraw_vesting import WithdrawVesting
from clive.__private.ui.operations.witness_block_approve.witness_block_approve import WitnessBlockApprove

OPERATIONS_AND_BUTTONS: Final[dict[str, Any]] = {
    "account-transfer-button": TransferToAccount,
    "savings-transfer-button": TransferToSavings,
    "vote-button": Vote,
    "convert-button": Convert,
    "account-witness-vote-button": AccountWitnessVote,
    "witness-block-approve-button": WitnessBlockApprove,
    "vesting-transfer-button": TransferToVesting,
    "account-witness-proxy-button": AccountWitnessProxy,
    "cancel-transfer-from-savings-button": CancelTransferFromSavings,
    "change-recovery-account-button": ChangeRecoveryAccount,
    "claim-account-button": ClaimAccount,
    "withdraw-vesting-button": WithdrawVesting,
    "update-proposal-votes-button": UpdateProposalVotes,
    "update-proposal-button": UpdateProposal,
    "transfer-from-savings-button": TransferFromSavings,
    "set-withdraw-vesting-route-button": SetWithdrawVestingRoute,
    "set-reset-account-button": SetResetAccount,
    "remove-proposal-button": RemoveProposal,
}
