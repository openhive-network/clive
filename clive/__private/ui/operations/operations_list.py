"""File with available operations and matching buttons."""
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
    from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
    from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen


FINANCIAL_OPERATIONS: Final[list[type[OperationBaseScreen]]] = [
    TransferToAccount,
]
RAW_OPERATIONS: Final[list[type[RawOperationBaseScreen]]] = [
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
    Vote,
    Comment,
    DeleteComment,
    CommentOptions,
    UpdateProposalVotes,
    WitnessSetProperties,
    WitnessUpdate,
    EscrowTransfer,
    EscrowDispute,
    RequestAccountRecovery,
    LimitOrderCancel,
    LimitOrderCreate,
    LimitOrderCreate2,
    RecoverAccount,
    AccountCreate,
    AccountUpdate,
    AccountUpdate2,
    AccountWitnessProxy,
    AccountWitnessVote,
    ChangeRecoveryAccount,
    ClaimAccount,
    CreateClaimedAccount,
    CustomJson,
    EscrowRelease,
]
