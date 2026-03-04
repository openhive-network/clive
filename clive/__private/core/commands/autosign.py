from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_in_unlocked import CommandInUnlocked
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.core.commands.prefetch_transaction_authorities import PrefetchTransactionAuthorities
from clive.__private.core.constants.authority import HIVE_MAX_SIG_CHECK_DEPTH
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.iwax import (
    calculate_sig_digest,
    collect_signing_keys,
    convert_schemas_account_to_python_authorities,
    get_transaction_required_authorities,
    minimize_required_signatures,
)
from clive.__private.core.keys.key_manager import KeyManager, KeyNotFoundError, MultipleKeysFoundError
from clive.__private.logger import logger
from clive.__private.models.transaction import Transaction
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    import wax
    from clive.__private.core.node import Node
    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.schemas import Signature


class AutoSignCommandError(CommandError):
    """Base error for all autosign related errors."""


class WrongAlreadySignedModeAutoSignError(AutoSignCommandError):
    def __init__(self, command: Command, already_signed_mode: AlreadySignedMode) -> None:
        self.already_signed_mode: AlreadySignedMode = already_signed_mode
        self.reason = f"Autosign cannot be used together with already_signed_mode {self.already_signed_mode}. "
        super().__init__(command, self.reason)


class TooManyKeysAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign cannot be used when there are multiple keys available."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class NoKeyAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign cannot be used when there is no key available."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class InsufficientKeysAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign failed: wallet keys satisfy only some of the transaction's required authorities."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


class AuthorityPrefetchAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Autosign failed: could not fetch required authorities from the node."

    def __init__(self, command: Command, cause: Exception) -> None:
        self.cause = cause
        super().__init__(command, self.REASON)


class TransactionAlreadySignedAutoSignError(AutoSignCommandError):
    REASON: Final[str] = "Your transaction is already signed."

    def __init__(self, command: Command) -> None:
        super().__init__(command, self.REASON)


@dataclass(kw_only=True)
class AutoSign(CommandInUnlocked, CommandWithResult[Transaction]):
    transaction: Transaction
    keys: KeyManager
    chain_id: str
    node: Node
    already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT
    """How to handle the situation when transaction is already signed."""

    async def _execute(self) -> None:
        self._throw_wrong_already_signed_mode()
        self._throw_is_transaction_already_signed()

        # remove this condition when wax autosign is fully rolled out and tested
        if safe_settings.use_wax_autosign:
            await self._sign_with_wax_autosign()
        else:
            await self._sign_with_single_key()

        self._result = self.transaction

    async def _sign_with_single_key(self) -> None:
        try:
            key = self.keys.unique_key
        except KeyNotFoundError:
            raise NoKeyAutoSignError(self) from None
        except MultipleKeysFoundError:
            raise TooManyKeysAutoSignError(self) from None

        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        result = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=key.value)
        self._set_transaction_signature(result)

    async def _sign_with_wax_autosign(self) -> None:
        try:
            cache = await PrefetchTransactionAuthorities(
                transaction=self.transaction, node=self.node
            ).execute_with_result()
        except Exception as error:
            raise AuthorityPrefetchAutoSignError(self, error) from error

        authorities_map: dict[str, wax.python_authorities] = {
            name: convert_schemas_account_to_python_authorities(account) for name, account in cache.items()
        }

        def retrieve_authorities(account_names: list[str]) -> dict[str, wax.python_authorities]:
            return {name: authorities_map[name] for name in account_names if name in authorities_map}

        required_keys = collect_signing_keys(self.transaction, retrieve_authorities)
        logger.debug(f"AutoSign: required signing keys: {required_keys}")

        profile_public_keys = [key.value for key in self.keys]
        matching_keys = [key for key in required_keys if key in profile_public_keys]
        logger.debug(f"AutoSign: matching keys in profile: {matching_keys}")

        if not self.check_authority(matching_keys, authorities_map):
            raise InsufficientKeysAutoSignError(self)

        sig_digest = calculate_sig_digest(self.transaction, self.chain_id)
        key_to_signature: dict[str, Signature] = {}
        for key in matching_keys:
            signature = await self.unlocked_wallet.sign_digest(sig_digest=sig_digest, key=key)
            key_to_signature[key] = signature
        self.transaction.signatures = list(key_to_signature.values())

        minimal_keys = self._minimize_signatures(matching_keys, authorities_map)
        self.transaction.signatures = [key_to_signature[key] for key in minimal_keys]

    def _minimize_signatures(
        self,
        matching_keys: list[str],
        authorities_map: dict[str, wax.python_authorities],
    ) -> list[str]:
        """Minimize signatures, falling back to all matching keys if minimization produces an insufficient result.

        Args:
            matching_keys: Public keys that match the transaction's required authorities.
            authorities_map: Mapping of account names to their authority structures.

        Returns:
            The minimal list of keys needed, or all matching keys if minimization fails.
        """
        minimal_keys = minimize_required_signatures(
            self.transaction,
            self.chain_id,
            matching_keys,
            authorities_map,
            lambda _witness: "",
        )

        if not self.check_authority(minimal_keys, authorities_map):
            logger.warning("AutoSign: minimization removed required keys, using all matching keys.")
            return matching_keys

        logger.debug(f"AutoSign: minimal keys after minimization: {minimal_keys}")
        return minimal_keys

    def check_authority(  # noqa: C901
        self,
        keys: list[str],
        authorities_map: dict[str, wax.python_authorities],
    ) -> bool:
        """Check that the given keys satisfy all required authorities for the transaction.

        Note: This check is not performed in cli_wallet (we rely on node checking there), but it allows us
        to raise InsufficientKeysAutoSignError early — surfacing a CLIPrettyError in CLI or a notification in TUI.

        Args:
            keys: Public keys to check against the transaction's required authorities.
            authorities_map: Mapping of account names to their authority structures.

        Returns:
            True if all required authorities are satisfied, False otherwise.
        """
        required_auths = get_transaction_required_authorities(self.transaction)
        key_set = set(keys)

        account_authority_checks: list[tuple[str, str, wax.python_authority]] = []
        for account_name in required_auths.active_accounts:
            auths = authorities_map.get(account_name)
            if auths is not None:
                account_authority_checks.append((account_name, "active", auths.active))
        for account_name in required_auths.posting_accounts:
            auths = authorities_map.get(account_name)
            if auths is not None:
                account_authority_checks.append((account_name, "posting", auths.posting))
        for account_name in required_auths.owner_accounts:
            auths = authorities_map.get(account_name)
            if auths is not None:
                account_authority_checks.append((account_name, "owner", auths.owner))

        for account_name, authority_type, authority in account_authority_checks:
            if not self._check_single_authority(authority, key_set, authorities_map):
                logger.debug(f"AutoSign: {authority_type} authority for '{account_name}' not satisfied")
                return False

        for i, authority in enumerate(required_auths.other_authorities):
            if not self._check_single_authority(authority, key_set, authorities_map):
                logger.debug(f"AutoSign: other authority [{i}] not satisfied")
                return False

        return True

    @staticmethod
    def _check_single_authority(
        authority: wax.python_authority,
        key_set: set[str],
        authorities_map: dict[str, wax.python_authorities],
        depth: int = 0,
    ) -> bool:
        """Recursively check if an authority is satisfied by the available keys, following account_auths chains.

        Args:
            authority: The authority structure to check against.
            key_set: Set of public keys available for signing.
            authorities_map: Mapping of account names to their authority structures.
            depth: Current recursion depth for account_auths traversal.

        Returns:
            True if the authority is satisfied by the available keys, False otherwise.
        """
        total_weight = sum(authority.key_auths.get(k, 0) for k in key_set)
        if total_weight >= authority.weight_threshold:
            return True

        if depth >= HIVE_MAX_SIG_CHECK_DEPTH:
            return False

        for aa_name, aa_weight in authority.account_auths.items():
            aa_auths = authorities_map.get(aa_name)
            if aa_auths is None:
                continue
            if AutoSign._check_single_authority(aa_auths.active, key_set, authorities_map, depth + 1):
                total_weight += aa_weight
                if total_weight >= authority.weight_threshold:
                    return True

        return False

    def _throw_wrong_already_signed_mode(self) -> None:
        if self.already_signed_mode == "strict":
            # autosign can be used only in `strict` mode
            return

        if self.already_signed_mode in ["multisign", "override"]:
            raise WrongAlreadySignedModeAutoSignError(self, self.already_signed_mode)

        raise NotImplementedError(f"Unknown already_signed_mode: {self.already_signed_mode}")

    def _throw_is_transaction_already_signed(self) -> None:
        if self.transaction.is_signed:
            raise TransactionAlreadySignedAutoSignError(self)

    def _set_transaction_signature(self, signature: Signature) -> None:
        self.transaction.signatures = [signature]
