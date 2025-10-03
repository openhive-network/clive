from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.si.core.generate import (
    GenerateKeyFromSeed,
    GeneratePublicKey,
    GenerateRandomKey,
    GenerateSecretPhrase,
)

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevel
    from clive.__private.si.data_classes import KeyPair


class GenerateInterface:
    """Interface for generating keys and secret phrases."""

    def __init__(self) -> None:
        pass

    def random_key(self, key_pairs: int = 1) -> list[KeyPair]:
        """Generate one or more random key pairs."""
        return GenerateRandomKey(key_pairs=key_pairs).run()

    def key_from_seed(
        self,
        account_name: str,
        password: str,
        role: AuthorityLevel,
        *,
        only_private_key: bool = False,
        only_public_key: bool = False,
    ) -> KeyPair:
        """Generate a key pair from a seed (account name, password, role)."""
        return GenerateKeyFromSeed(
            account_name=account_name,
            password=password,
            role=role,
            only_private_key=only_private_key,
            only_public_key=only_public_key,
        ).run()

    def public_key(self, private_key: str) -> str:
        """Get the public key for a given private key."""
        return GeneratePublicKey(private_key=private_key).run()

    def secret_phrase(self) -> str:
        """Generate a new secret phrase."""
        return GenerateSecretPhrase().run()
