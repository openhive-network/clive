"""File with available operations and matching buttons"""
from __future__ import annotations

from typing import TYPE_CHECKING, Final

from clive.__private.ui.operations import (
    AccountCreate,
    AccountUpdate,
    AccountUpdate2,
    AccountWitnessProxy,
    AccountWitnessVote,
    CancelTransferFromSavings,
    ChangeRecoveryAccount,
    ClaimAccount,
    ClaimRewardBalance,
    CollateralizedConvert,
    Comment,
    CommentOptions,
    Convert,
    CreateClaimedAccount,
    CreateProposal,
    Custom,
    CustomJson,
    DelegateVestingShares,
    DeleteComment,
    EscrowDispute,
    EscrowRelease,
    EscrowTransfer,
    LimitOrderCancel,
    LimitOrderCreate,
    LimitOrderCreate2,
    RecoverAccount,
    RecurrentTransfer,
    RemoveProposal,
    RequestAccountRecovery,
    SetWithdrawVestingRoute,
    TransferFromSavings,
    TransferToAccount,
    TransferToSavings,
    TransferToVesting,
    UpdateProposal,
    UpdateProposalVotes,
    Vote,
    WithdrawVesting,
    WitnessSetProperties,
    WitnessUpdate,
)

if TYPE_CHECKING:
    from clive.__private.ui.operations.operation_base import OperationBase


SOCIAL_OPERATIONS: Final[list[type[OperationBase]]] = [
    Vote,
    Comment,
    DeleteComment,
    CommentOptions,
]
FINANCIAL_OPERATIONS: Final[list[type[OperationBase]]] = [
    TransferToAccount,
    TransferToVesting,
    WithdrawVesting,
    Convert,
    SetWithdrawVestingRoute,
    TransferToSavings,
    TransferFromSavings,
    CancelTransferFromSavings,
    ClaimRewardBalance,
    CollateralizedConvert,
    DelegateVestingShares,
    RecurrentTransfer,
    EscrowTransfer,
    EscrowDispute,
    EscrowRelease,
    LimitOrderCancel,
    LimitOrderCreate,
    LimitOrderCreate2,
]
GOVERNANCE_OPERATIONS: Final[list[type[OperationBase]]] = [
    AccountWitnessVote,
    AccountWitnessProxy,
    WitnessSetProperties,
    WitnessUpdate,
    UpdateProposalVotes,
    CreateProposal,
    RemoveProposal,
    UpdateProposal,
]
ACCOUNT_MANAGEMENT: Final[list[type[OperationBase]]] = [
    AccountCreate,
    AccountUpdate,
    AccountUpdate2,
    ChangeRecoveryAccount,
    ClaimAccount,
    CreateClaimedAccount,
    RecoverAccount,
    RequestAccountRecovery,
]
CUSTOM_OPERATIONS: Final[list[type[OperationBase]]] = [CustomJson, Custom]
