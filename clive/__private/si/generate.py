from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.si.core.generate import GenerateRandomKey

if TYPE_CHECKING:
    from clive.__private.si.data_classes import KeyPair


class GenerateInterface:
    """Interface for generating keys and secret phrases."""

    def __init__(self) -> None:
        pass

    async def random_key(self, key_pairs: int = 1) -> list[KeyPair]:
        """Generate one or more random key pairs."""
        return await GenerateRandomKey(key_pairs=key_pairs).run()
