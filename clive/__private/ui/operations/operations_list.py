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
    RequestAccountRecovery,
    SetWithdrawVestingRoute,
    TransferFromSavings,
    TransferToAccount,
    TransferToSavings,
    TransferToVesting,
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
]
GOVERNANCE_OPERATIONS: Final[list[type[OperationBase]]] = [
    AccountWitnessVote,
    AccountWitnessProxy,
    UpdateProposalVotes,
]
ADVANCED_OPERATIONS: Final[list[type[OperationBase]]] = [
    AccountCreate,
    CustomJson,
    ClaimAccount,
    CreateClaimedAccount,
    RequestAccountRecovery,
    RecoverAccount,
    ChangeRecoveryAccount,
    EscrowTransfer,
    EscrowDispute,
    EscrowRelease,
]
MARKET_OPERATIONS: Final[list[type[OperationBase]]] = [LimitOrderCreate, LimitOrderCreate2, LimitOrderCancel]
WITNESS_OPERATIONS: Final[list[type[OperationBase]]] = [
    WitnessUpdate,
    WitnessSetProperties,
]
ACCOUNT_MANAGEMENT: Final[list[type[OperationBase]]] = [
    AccountUpdate,
    AccountUpdate2,
]
