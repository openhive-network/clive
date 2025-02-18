from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.models import schemas


class OperationVisitor:
    def visit(self, operation: schemas.OperationUnion) -> None:
        """Determine the correct method to call based on operation type."""
        method_name = f"visit_{operation.get_name_with_suffix()}"
        visit_method = getattr(self, method_name, self._default_visit)
        visit_method(operation)

    def visit_account_create_operation(self, operation: schemas.AccountCreateOperation) -> None:
        """Visitor for AccountCreateOperation operation."""
        self._default_visit(operation)

    def visit_account_create_with_delegation_operation(
        self, operation: schemas.AccountCreateWithDelegationOperation
    ) -> None:
        """Visitor for AccountCreateWithDelegationOperation operation."""
        self._default_visit(operation)

    def visit_account_update2_operation(self, operation: schemas.AccountUpdate2Operation) -> None:
        """Visitor for AccountUpdate2Operation operation."""
        self._default_visit(operation)

    def visit_account_update_operation(self, operation: schemas.AccountUpdateOperation) -> None:
        """Visitor for AccountUpdateOperation operation."""
        self._default_visit(operation)

    def visit_account_witness_proxy_operation(self, operation: schemas.AccountWitnessProxyOperation) -> None:
        """Visitor for AccountWitnessProxyOperation operation."""
        self._default_visit(operation)

    def visit_account_witness_vote_operation(self, operation: schemas.AccountWitnessVoteOperation) -> None:
        """Visitor for AccountWitnessVoteOperation operation."""
        self._default_visit(operation)

    def visit_cancel_transfer_from_savings_operation(
        self, operation: schemas.CancelTransferFromSavingsOperation
    ) -> None:
        """Visitor for CancelTransferFromSavingsOperation operation."""
        self._default_visit(operation)

    def visit_change_recovery_account_operation(self, operation: schemas.ChangeRecoveryAccountOperation) -> None:
        """Visitor for ChangeRecoveryAccountOperation operation."""
        self._default_visit(operation)

    def visit_claim_account_operation(self, operation: schemas.ClaimAccountOperation) -> None:
        """Visitor for ClaimAccountOperation operation."""
        self._default_visit(operation)

    def visit_claim_reward_balance_operation(self, operation: schemas.ClaimRewardBalanceOperation) -> None:
        """Visitor for ClaimRewardBalanceOperation operation."""
        self._default_visit(operation)

    def visit_collateralized_convert_operation(self, operation: schemas.CollateralizedConvertOperation) -> None:
        """Visitor for CollateralizedConvertOperation operation."""
        self._default_visit(operation)

    def visit_comment_operation(self, operation: schemas.CommentOperation) -> None:
        """Visitor for CommentOperation operation."""
        self._default_visit(operation)

    def visit_comment_options_operation(self, operation: schemas.CommentOptionsOperation) -> None:
        """Visitor for CommentOptionsOperation operation."""
        self._default_visit(operation)

    def visit_convert_operation(self, operation: schemas.ConvertOperation) -> None:
        """Visitor for ConvertOperation operation."""
        self._default_visit(operation)

    def visit_create_claimed_account_operation(self, operation: schemas.CreateClaimedAccountOperation) -> None:
        """Visitor for CreateClaimedAccountOperation operation."""
        self._default_visit(operation)

    def visit_create_proposal_operation(self, operation: schemas.CreateProposalOperation) -> None:
        """Visitor for CreateProposalOperation operation."""
        self._default_visit(operation)

    def visit_custom_binary_operation(self, operation: schemas.CustomBinaryOperation) -> None:
        """Visitor for CustomBinaryOperation operation."""
        self._default_visit(operation)

    def visit_custom_json_operation(self, operation: schemas.CustomJsonOperation) -> None:
        """Visitor for CustomJsonOperation operation."""
        self._default_visit(operation)

    def visit_custom_operation(self, operation: schemas.CustomOperation) -> None:
        """Visitor for CustomOperation operation."""
        self._default_visit(operation)

    def visit_decline_voting_rights_operation(self, operation: schemas.DeclineVotingRightsOperation) -> None:
        """Visitor for DeclineVotingRightsOperation operation."""
        self._default_visit(operation)

    def visit_delegate_vesting_shares_operation(self, operation: schemas.DelegateVestingSharesOperation) -> None:
        """Visitor for DelegateVestingSharesOperation operation."""
        self._default_visit(operation)

    def visit_delete_comment_operation(self, operation: schemas.DeleteCommentOperation) -> None:
        """Visitor for DeleteCommentOperation operation."""
        self._default_visit(operation)

    def visit_escrow_approve_operation(self, operation: schemas.EscrowApproveOperation) -> None:
        """Visitor for EscrowApproveOperation operation."""
        self._default_visit(operation)

    def visit_escrow_dispute_operation(self, operation: schemas.EscrowDisputeOperation) -> None:
        """Visitor for EscrowDisputeOperation operation."""
        self._default_visit(operation)

    def visit_escrow_release_operation(self, operation: schemas.EscrowReleaseOperation) -> None:
        """Visitor for EscrowReleaseOperation operation."""
        self._default_visit(operation)

    def visit_escrow_transfer_operation(self, operation: schemas.EscrowTransferOperation) -> None:
        """Visitor for EscrowTransferOperation operation."""
        self._default_visit(operation)

    def visit_feed_publish_operation(self, operation: schemas.FeedPublishOperation) -> None:
        """Visitor for FeedPublishOperation operation."""
        self._default_visit(operation)

    def visit_limit_order_cancel_operation(self, operation: schemas.LimitOrderCancelOperation) -> None:
        """Visitor for LimitOrderCancelOperation operation."""
        self._default_visit(operation)

    def visit_limit_order_create_2_operation(self, operation: schemas.LimitOrderCreate2Operation) -> None:
        """Visitor for LimitOrderCreate2Operation operation."""
        self._default_visit(operation)

    def visit_limit_order_create_operation(self, operation: schemas.LimitOrderCreateOperation) -> None:
        """Visitor for LimitOrderCreateOperation operation."""
        self._default_visit(operation)

    def visit_pow_operation(self, operation: schemas.PowOperation) -> None:
        """Visitor for PowOperation operation."""
        self._default_visit(operation)

    def visit_pow_2_operation(self, operation: schemas.Pow2Operation) -> None:
        """Visitor for Pow2Operation operation."""
        self._default_visit(operation)

    def visit_recover_account_operation(self, operation: schemas.RecoverAccountOperation) -> None:
        """Visitor for RecoverAccountOperation operation."""
        self._default_visit(operation)

    def visit_recurrent_transfer_operation(self, operation: schemas.RecurrentTransferOperation) -> None:
        """Visitor for RecurrentTransferOperation operation."""
        self._default_visit(operation)

    def visit_remove_proposal_operation(self, operation: schemas.RemoveProposalOperation) -> None:
        """Visitor for RemoveProposalOperation operation."""
        self._default_visit(operation)

    def visit_request_account_recovery_operation(self, operation: schemas.RequestAccountRecoveryOperation) -> None:
        """Visitor for RequestAccountRecoveryOperation operation."""
        self._default_visit(operation)

    def visit_reset_account_operation(self, operation: schemas.ResetAccountOperation) -> None:
        """Visitor for ResetAccountOperation operation."""
        self._default_visit(operation)

    def visit_set_reset_account_operation(self, operation: schemas.SetResetAccountOperation) -> None:
        """Visitor for SetResetAccountOperation operation."""
        self._default_visit(operation)

    def visit_set_withdraw_vesting_route_operation(self, operation: schemas.SetWithdrawVestingRouteOperation) -> None:
        """Visitor for SetWithdrawVestingRouteOperation operation."""
        self._default_visit(operation)

    def visit_transfer_from_savings_operation(self, operation: schemas.TransferFromSavingsOperation) -> None:
        """Visitor for TransferFromSavingsOperation operation."""
        self._default_visit(operation)

    def visit_transfer_operation(self, operation: schemas.TransferOperation) -> None:
        """Visitor for TransferOperation operation."""
        self._default_visit(operation)

    def visit_transfer_to_savings_operation(self, operation: schemas.TransferToSavingsOperation) -> None:
        """Visitor for TransferToSavingsOperation operation."""
        self._default_visit(operation)

    def visit_transfer_to_vesting_operation(self, operation: schemas.TransferToVestingOperation) -> None:
        """Visitor for TransferToVestingOperation operation."""
        self._default_visit(operation)

    def visit_update_proposal_operation(self, operation: schemas.UpdateProposalOperation) -> None:
        """Visitor for UpdateProposalOperation operation."""
        self._default_visit(operation)

    def visit_update_proposal_votes_operation(self, operation: schemas.UpdateProposalVotesOperation) -> None:
        """Visitor for UpdateProposalVotesOperation operation."""
        self._default_visit(operation)

    def visit_vote_operation(self, operation: schemas.VoteOperation) -> None:
        """Visitor for VoteOperation operation."""
        self._default_visit(operation)

    def visit_withdraw_vesting_operation(self, operation: schemas.WithdrawVestingOperation) -> None:
        """Visitor for WithdrawVestingOperation operation."""
        self._default_visit(operation)

    def visit_witness_block_approve_operation(self, operation: schemas.WitnessBlockApproveOperation) -> None:
        """Visitor for WitnessBlockApproveOperation operation."""
        self._default_visit(operation)

    def visit_witness_set_properties_operation(self, operation: schemas.WitnessSetPropertiesOperation) -> None:
        """Visitor for WitnessSetPropertiesOperation operation."""
        self._default_visit(operation)

    def visit_witness_update_operation(self, operation: schemas.WitnessUpdateOperation) -> None:
        """Visitor for WitnessUpdateOperation operation."""
        self._default_visit(operation)

    def _default_visit(self, operation: schemas.OperationUnion) -> None:
        """Fallback if no specific method exists for an operation type."""
