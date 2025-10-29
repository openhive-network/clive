from __future__ import annotations

from typing import TYPE_CHECKING

from schemas.operations import AccountUpdate2Operation
from wax._private.models.hive_date_time import HiveDateTime
from wax.interfaces import IAuthorityDataProvider
from wax.models.authority import WaxAccountAuthorityInfo, WaxAuthorities, WaxAuthority

if TYPE_CHECKING:
    from clive.__private.models.schemas import Account, Authority
    from wax.models.basic import AccountName
    from clive.__private.core.commands.data_retrieval.update_node_data import NodeData
    from clive.__private.models.transaction import Transaction


class CliveAuthorityDataProvider(IAuthorityDataProvider):
    """
    Provides authority data for Hive accounts using the wax interface.

    Args:
        account_data: account data collected with find_accounts from database api
    """

    def __init__(self, account_data: Account) -> None:
        self._account_data = account_data

    async def get_hive_authority_data(self, name: AccountName) -> WaxAccountAuthorityInfo:
        def convert_list_of_tuples_to_mapping(entry_list: list[tuple[str, int]]) -> dict[str, int]:
            result: dict[str, int] = {}
            for key, value in entry_list:
                assert key not in result, f"Duplicate key '{key}' found in authority entries."
                result[key] = value
            return result

        def convert_schemas_authority_to_wax_authority(schemas_authority: Authority) -> WaxAuthority:
            """
            Form of key_auths and account_auths properties differs between schemas authority object and wax one.

            Args:
                schemas_authority: Authority in schemas type to convert

            Returns:
                Converted authority to wax format.

            """
            return WaxAuthority(
                weight_threshold=schemas_authority.weight_threshold,
                account_auths=convert_list_of_tuples_to_mapping(schemas_authority.account_auths),
                key_auths=convert_list_of_tuples_to_mapping(schemas_authority.key_auths),
            )

        assert name == self._account_data.name, (
            f"You provided account data for the wrong account got `{self._account_data.name}` expected `{name}`."
        )

        authorities = WaxAuthorities(
            owner=convert_schemas_authority_to_wax_authority(self._account_data.owner),
            active=convert_schemas_authority_to_wax_authority(self._account_data.active),
            posting=convert_schemas_authority_to_wax_authority(self._account_data.posting),
        )

        return WaxAccountAuthorityInfo(
            account=self._account_data.name,
            authorities=authorities,
            memo_key=self._account_data.memo_key,
            last_owner_update=HiveDateTime(self._account_data.last_owner_update),
            previous_owner_update=HiveDateTime(self._account_data.previous_owner_update),
        )
    

class CliveAuthorityDataProviderWithTransactionData(IAuthorityDataProvider):
    """
    Provides authority data for Hive accounts using the wax interface and transaction from profile.

    Args:
        account_data: account data from profile (from database api call)
        transaction: transaction from profile with possible account_update2 operations that will fill authority data
    """

    def __init__(self, account_data: NodeData, transaction: Transaction) -> None:
        self._account_data = account_data
        self._transaction = transaction


    async def get_hive_authority_data(self, name: AccountName) -> WaxAccountAuthorityInfo:
        assert name == self._account_data.authority.name, (
            f"You provided account data for the wrong account got `{self._account_data.name}` expected `{name}`."
        )

        # extract operations from transaction - filter only acount update2, extract modified authorities from it
        account_update2_operations: list[AccountUpdate2Operation] | None = None
        account_update2_operations = [operation for operation in self._transaction.operations_models if isinstance(operation, AccountUpdate2Operation)]
        if not account_update2_operations:
            # no account update2 operations in transaction - skip filling
            ...
        else:
            ...

