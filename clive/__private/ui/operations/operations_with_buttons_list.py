"""File with available operations and matching buttons"""
from __future__ import annotations

from typing import Any, Final

from clive.__private.ui.operations import (
    AccountWitnessProxy,
    AccountWitnessVote,
    CancelTransferFromSavings,
    ChangeRecoveryAccount,
    ClaimAccount,
    ClaimRewardBalance,
    Comment,
    CommentOptions,
    Convert,
    CreateProposal,
    Custom,
    CustomJson,
    DeclineVotingRights,
    DelegateVestingShares,
    DeleteComment,
    EscrowApprove,
    EscrowDispute,
    EscrowRelease,
    EscrowTransfer,
    LimitOrderCancel,
    LimitOrderCreate,
    RecurrentTransfer,
    RemoveProposal,
    ResetAccount,
    SetResetAccount,
    SetWithdrawVestingRoute,
    TransferFromSavings,
    TransferToAccount,
    TransferToSavings,
    TransferToVesting,
    UpdateProposal,
    UpdateProposalVotes,
    Vote,
    WithdrawVesting,
    WitnessBlockApprove,
    WitnessSetProperties,
    WitnessUpdate,
)

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
    "recurrent-transfer-button": RecurrentTransfer,
    "limit-order-create-button": LimitOrderCreate,
    "limit-order-cancel-button": LimitOrderCancel,
    "escrow-transfer-button": EscrowTransfer,
    "escrow-release-button": EscrowRelease,
    "escrow-dispute-button": EscrowDispute,
    "escrow-approve-button": EscrowApprove,
    "delete-comment-button": DeleteComment,
    "delegate-vesting-shares-button": DelegateVestingShares,
    "decline-voting-rights-button": DeclineVotingRights,
    "custom-button": Custom,
    "custom-json-button": CustomJson,
    "create-proposal-button": CreateProposal,
    "comment-options-button": CommentOptions,
    "comment-button": Comment,
    "claim-reward-balance-button": ClaimRewardBalance,
    "witness-update-button": WitnessUpdate,
    "witness-set-properties-button": WitnessSetProperties,
    "reset-account-button": ResetAccount,
}
