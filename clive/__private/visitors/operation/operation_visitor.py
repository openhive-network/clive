from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.models.schemas import (
        AccountCreateOperation,
        AccountCreateWithDelegationOperation,
        AccountUpdate2Operation,
        AccountUpdateOperation,
        AccountWitnessProxyOperation,
        AccountWitnessVoteOperation,
        CancelTransferFromSavingsOperation,
        ChangeRecoveryAccountOperation,
        ClaimAccountOperation,
        ClaimRewardBalanceOperation,
        CollateralizedConvertOperation,
        CommentOperation,
        CommentOptionsOperation,
        ConvertOperation,
        CreateClaimedAccountOperation,
        CreateProposalOperation,
        CustomBinaryOperation,
        CustomJsonOperation,
        CustomOperation,
        DeclineVotingRightsOperation,
        DelegateVestingSharesOperation,
        DeleteCommentOperation,
        EscrowApproveOperation,
        EscrowDisputeOperation,
        EscrowReleaseOperation,
        EscrowTransferOperation,
        FeedPublishOperation,
        LimitOrderCancelOperation,
        LimitOrderCreate2Operation,
        LimitOrderCreateOperation,
        OperationUnion,
        Pow2Operation,
        PowOperation,
        RecoverAccountOperation,
        RecurrentTransferOperation,
        RemoveProposalOperation,
        RequestAccountRecoveryOperation,
        ResetAccountOperation,
        SetResetAccountOperation,
        SetWithdrawVestingRouteOperation,
        TransferFromSavingsOperation,
        TransferOperation,
        TransferToSavingsOperation,
        TransferToVestingOperation,
        UpdateProposalOperation,
        UpdateProposalVotesOperation,
        VoteOperation,
        WithdrawVestingOperation,
        WitnessBlockApproveOperation,
        WitnessSetPropertiesOperation,
        WitnessUpdateOperation,
    )


class OperationVisitor:
    def _default_visit(self, operation: OperationUnion) -> None:
        """Fallback if no specific method exists for an operation type."""

    def visit(self, operation: OperationUnion) -> None:
        """Determine the correct method to call based on operation type."""
        operation_name = operation.get_name_with_suffix()
        method_name = f"visit_{operation_name}"
        visit_method = getattr(self, method_name, None)
        assert visit_method is not None, f"No visit method defined for {operation_name}"
        visit_method(operation)

    def visit_account_create_operation(self, operation: AccountCreateOperation) -> None:
        """Visitor for AccountCreateOperation operation."""
        self._default_visit(operation)

    def visit_account_create_with_delegation_operation(self, operation: AccountCreateWithDelegationOperation) -> None:
        """Visitor for AccountCreateWithDelegationOperation operation."""
        self._default_visit(operation)

    def visit_account_update2_operation(self, operation: AccountUpdate2Operation) -> None:
        """Visitor for AccountUpdate2Operation operation."""
        self._default_visit(operation)

    def visit_account_update_operation(self, operation: AccountUpdateOperation) -> None:
        """Visitor for AccountUpdateOperation operation."""
        self._default_visit(operation)

    def visit_account_witness_proxy_operation(self, operation: AccountWitnessProxyOperation) -> None:
        """Visitor for AccountWitnessProxyOperation operation."""
        self._default_visit(operation)

    def visit_account_witness_vote_operation(self, operation: AccountWitnessVoteOperation) -> None:
        """Visitor for AccountWitnessVoteOperation operation."""
        self._default_visit(operation)

    def visit_cancel_transfer_from_savings_operation(self, operation: CancelTransferFromSavingsOperation) -> None:
        """Visitor for CancelTransferFromSavingsOperation operation."""
        self._default_visit(operation)

    def visit_change_recovery_account_operation(self, operation: ChangeRecoveryAccountOperation) -> None:
        """Visitor for ChangeRecoveryAccountOperation operation."""
        self._default_visit(operation)

    def visit_claim_account_operation(self, operation: ClaimAccountOperation) -> None:
        """Visitor for ClaimAccountOperation operation."""
        self._default_visit(operation)

    def visit_claim_reward_balance_operation(self, operation: ClaimRewardBalanceOperation) -> None:
        """Visitor for ClaimRewardBalanceOperation operation."""
        self._default_visit(operation)

    def visit_collateralized_convert_operation(self, operation: CollateralizedConvertOperation) -> None:
        """Visitor for CollateralizedConvertOperation operation."""
        self._default_visit(operation)

    def visit_comment_operation(self, operation: CommentOperation) -> None:
        """Visitor for CommentOperation operation."""
        self._default_visit(operation)

    def visit_comment_options_operation(self, operation: CommentOptionsOperation) -> None:
        """Visitor for CommentOptionsOperation operation."""
        self._default_visit(operation)

    def visit_convert_operation(self, operation: ConvertOperation) -> None:
        """Visitor for ConvertOperation operation."""
        self._default_visit(operation)

    def visit_create_claimed_account_operation(self, operation: CreateClaimedAccountOperation) -> None:
        """Visitor for CreateClaimedAccountOperation operation."""
        self._default_visit(operation)

    def visit_create_proposal_operation(self, operation: CreateProposalOperation) -> None:
        """Visitor for CreateProposalOperation operation."""
        self._default_visit(operation)

    def visit_custom_binary_operation(self, operation: CustomBinaryOperation) -> None:
        """Visitor for CustomBinaryOperation operation."""
        self._default_visit(operation)

    def visit_custom_json_operation(self, operation: CustomJsonOperation) -> None:
        """Visitor for CustomJsonOperation operation."""
        self._default_visit(operation)

    def visit_custom_operation(self, operation: CustomOperation) -> None:
        """Visitor for CustomOperation operation."""
        self._default_visit(operation)

    def visit_decline_voting_rights_operation(self, operation: DeclineVotingRightsOperation) -> None:
        """Visitor for DeclineVotingRightsOperation operation."""
        self._default_visit(operation)

    def visit_delegate_vesting_shares_operation(self, operation: DelegateVestingSharesOperation) -> None:
        """Visitor for DelegateVestingSharesOperation operation."""
        self._default_visit(operation)

    def visit_delete_comment_operation(self, operation: DeleteCommentOperation) -> None:
        """Visitor for DeleteCommentOperation operation."""
        self._default_visit(operation)

    def visit_escrow_approve_operation(self, operation: EscrowApproveOperation) -> None:
        """Visitor for EscrowApproveOperation operation."""
        self._default_visit(operation)

    def visit_escrow_dispute_operation(self, operation: EscrowDisputeOperation) -> None:
        """Visitor for EscrowDisputeOperation operation."""
        self._default_visit(operation)

    def visit_escrow_release_operation(self, operation: EscrowReleaseOperation) -> None:
        """Visitor for EscrowReleaseOperation operation."""
        self._default_visit(operation)

    def visit_escrow_transfer_operation(self, operation: EscrowTransferOperation) -> None:
        """Visitor for EscrowTransferOperation operation."""
        self._default_visit(operation)

    def visit_feed_publish_operation(self, operation: FeedPublishOperation) -> None:
        """Visitor for FeedPublishOperation operation."""
        self._default_visit(operation)

    def visit_limit_order_cancel_operation(self, operation: LimitOrderCancelOperation) -> None:
        """Visitor for LimitOrderCancelOperation operation."""
        self._default_visit(operation)

    def visit_limit_order_create_2_operation(self, operation: LimitOrderCreate2Operation) -> None:
        """Visitor for LimitOrderCreate2Operation operation."""
        self._default_visit(operation)

    def visit_limit_order_create_operation(self, operation: LimitOrderCreateOperation) -> None:
        """Visitor for LimitOrderCreateOperation operation."""
        self._default_visit(operation)

    def visit_pow_operation(self, operation: PowOperation) -> None:
        """Visitor for PowOperation operation."""
        self._default_visit(operation)

    def visit_pow_2_operation(self, operation: Pow2Operation) -> None:
        """Visitor for Pow2Operation operation."""
        self._default_visit(operation)

    def visit_recover_account_operation(self, operation: RecoverAccountOperation) -> None:
        """Visitor for RecoverAccountOperation operation."""
        self._default_visit(operation)

    def visit_recurrent_transfer_operation(self, operation: RecurrentTransferOperation) -> None:
        """Visitor for RecurrentTransferOperation operation."""
        self._default_visit(operation)

    def visit_remove_proposal_operation(self, operation: RemoveProposalOperation) -> None:
        """Visitor for RemoveProposalOperation operation."""
        self._default_visit(operation)

    def visit_request_account_recovery_operation(self, operation: RequestAccountRecoveryOperation) -> None:
        """Visitor for RequestAccountRecoveryOperation operation."""
        self._default_visit(operation)

    def visit_reset_account_operation(self, operation: ResetAccountOperation) -> None:
        """Visitor for ResetAccountOperation operation."""
        self._default_visit(operation)

    def visit_set_reset_account_operation(self, operation: SetResetAccountOperation) -> None:
        """Visitor for SetResetAccountOperation operation."""
        self._default_visit(operation)

    def visit_set_withdraw_vesting_route_operation(self, operation: SetWithdrawVestingRouteOperation) -> None:
        """Visitor for SetWithdrawVestingRouteOperation operation."""
        self._default_visit(operation)

    def visit_transfer_from_savings_operation(self, operation: TransferFromSavingsOperation) -> None:
        """Visitor for TransferFromSavingsOperation operation."""
        self._default_visit(operation)

    def visit_transfer_operation(self, operation: TransferOperation) -> None:
        """Visitor for TransferOperation operation."""
        self._default_visit(operation)

    def visit_transfer_to_savings_operation(self, operation: TransferToSavingsOperation) -> None:
        """Visitor for TransferToSavingsOperation operation."""
        self._default_visit(operation)

    def visit_transfer_to_vesting_operation(self, operation: TransferToVestingOperation) -> None:
        """Visitor for TransferToVestingOperation operation."""
        self._default_visit(operation)

    def visit_update_proposal_operation(self, operation: UpdateProposalOperation) -> None:
        """Visitor for UpdateProposalOperation operation."""
        self._default_visit(operation)

    def visit_update_proposal_votes_operation(self, operation: UpdateProposalVotesOperation) -> None:
        """Visitor for UpdateProposalVotesOperation operation."""
        self._default_visit(operation)

    def visit_vote_operation(self, operation: VoteOperation) -> None:
        """Visitor for VoteOperation operation."""
        self._default_visit(operation)

    def visit_withdraw_vesting_operation(self, operation: WithdrawVestingOperation) -> None:
        """Visitor for WithdrawVestingOperation operation."""
        self._default_visit(operation)

    def visit_witness_block_approve_operation(self, operation: WitnessBlockApproveOperation) -> None:
        """Visitor for WitnessBlockApproveOperation operation."""
        self._default_visit(operation)

    def visit_witness_set_properties_operation(self, operation: WitnessSetPropertiesOperation) -> None:
        """Visitor for WitnessSetPropertiesOperation operation."""
        self._default_visit(operation)

    def visit_witness_update_operation(self, operation: WitnessUpdateOperation) -> None:
        """Visitor for WitnessUpdateOperation operation."""
        self._default_visit(operation)
