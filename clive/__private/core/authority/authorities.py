from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime  # noqa: TCH003
from enum import Enum
from typing import TYPE_CHECKING

from clive.__private.core.keys.key_manager import KeyNotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive.__private.core.types import AuthorityType
    from clive.models.aliased import Authority as SchemasAuthority


class State(Enum):
    NOT_USED = 1
    TO_BE_ADDED = 2
    ALREADY_USED = 3
    TO_BE_REMOVED = 4


@dataclass(kw_only=True, frozen=True)
class Authority:
    weight_threshold: int
    account_auths: list[tuple[str, int]]
    key_auths: list[tuple[str, int]]

    @classmethod
    def from_schemas_authority(cls, schemas_authority: SchemasAuthority) -> Authority:
        account_auths = [(str(account_name), int(weight)) for account_name, weight in schemas_authority.account_auths]
        key_auths = [(str(key), int(weight)) for key, weight in schemas_authority.key_auths]
        return cls(
            weight_threshold=schemas_authority.weight_threshold,
            account_auths=account_auths,
            key_auths=key_auths,
        )


class RoleSignature:
    @dataclass(kw_only=True, frozen=True)
    class AccountAuth:
        role_signature: RoleSignature
        name: str
        weight: int

        def __str__(self) -> str:
            return f"name: {self.name} weight: {self.weight}"

    @dataclass(kw_only=True, frozen=True)
    class KeyAuth:
        key: str
        weight: int
        state: State

        def set_state(self, value: State) -> None:
            object.__setattr__(self, "state", value)

        def __str__(self) -> str:
            return f"key: {self.key[:10]}... weight: {self.weight} state: {self.state}"

    def __init__(self, name: str, role: AuthorityType, required_weight: int) -> None:
        self._name = name
        self._role = role
        self._satisfied_weight = 0
        self._required_weight = required_weight
        self._account_auths: list[RoleSignature.AccountAuth] = []
        self._key_auths: list[RoleSignature.KeyAuth] = []

    def _get_key_auths(self, key: str) -> list[RoleSignature.KeyAuth]:
        key_auths = [key_auth for key_auth in self._key_auths if key_auth.key == key]
        for account_auth in self._account_auths:
            account_authority_key_auths = account_auth.role_signature._get_key_auths(key)
            key_auths.extend(account_authority_key_auths)
        return key_auths

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> AuthorityType:
        return self._role

    @property
    def satisfied_weight(self) -> int:
        return self._satisfied_weight

    @property
    def required_weight(self) -> int:
        return self._required_weight

    @property
    def account_auths(self) -> list[RoleSignature.AccountAuth]:
        return self._account_auths

    @property
    def key_auths(self) -> list[RoleSignature.KeyAuth]:
        return self._key_auths

    def is_weight_satisfied(self) -> bool:
        return self._satisfied_weight >= self._required_weight

    def _update_satisfied_weight(self) -> None:
        new_satisfied_weight = 0
        for account_auth in self._account_auths:
            account_auth.role_signature._update_satisfied_weight()
            if account_auth.role_signature.is_weight_satisfied():
                new_satisfied_weight += account_auth.weight
        for key_auth in self._key_auths:
            if key_auth.state in {State.TO_BE_ADDED, State.ALREADY_USED}:
                new_satisfied_weight += key_auth.weight
        self._satisfied_weight = new_satisfied_weight

    @staticmethod
    def create_filled_role_signature(name: str, role: AuthorityType, lut: dict[str, Authority]) -> RoleSignature:
        required_weight = lut[name].weight_threshold
        role_signature = RoleSignature(name, role, required_weight)
        for other_account_name, weight in lut[name].account_auths:
            if other_account_name in lut:
                other_account_role_signature = RoleSignature.create_filled_role_signature(other_account_name, role, lut)
                account_auth = RoleSignature.AccountAuth(
                    role_signature=other_account_role_signature, name=other_account_name, weight=weight
                )
                role_signature._account_auths.append(account_auth)
        for key, weight in lut[name].key_auths:
            key_auth = RoleSignature.KeyAuth(key=key, weight=weight, state=State.NOT_USED)
            role_signature._key_auths.append(key_auth)
        return role_signature

    def __iter__(self) -> Iterator[RoleSignature.AccountAuth | RoleSignature.KeyAuth]:
        for account_auth in self._account_auths:
            yield account_auth
            yield from account_auth.role_signature
        yield from self._key_auths


@dataclass(kw_only=True)
class AuthorityRootNode:
    owner: RoleSignature
    active: RoleSignature
    posting: RoleSignature

    def get_key_auths(self, key: str) -> list[RoleSignature.KeyAuth]:
        key_auths = self.owner._get_key_auths(key)
        key_auths.extend(self.active._get_key_auths(key))
        key_auths.extend(self.posting._get_key_auths(key))
        if key_auths == []:
            raise KeyNotFoundError
        return key_auths

    def set_key_state(self, key: str, state: State) -> None:
        key_auths = self.get_key_auths(key)
        for key_auth in key_auths:
            key_auth.set_state(state)
        self.owner._update_satisfied_weight()
        self.active._update_satisfied_weight()
        self.posting._update_satisfied_weight()

    def get_key_state(self, key: str) -> State:
        key_auths = self.get_key_auths(key)
        if key_auths == []:
            raise KeyNotFoundError
        # all key_auths have the same state
        return key_auths[0].state

    def __iter__(self) -> Iterator[RoleSignature.AccountAuth | RoleSignature.KeyAuth]:
        yield from self.owner
        yield from self.active
        yield from self.posting


@dataclass(kw_only=True, frozen=True)
class AllAuthorities:
    name: str
    owner: Authority
    active: Authority
    posting: Authority
    owner_lut: dict[str, Authority] = field(default_factory=dict)
    active_lut: dict[str, Authority] = field(default_factory=dict)
    posting_lut: dict[str, Authority] = field(default_factory=dict)
    last_updated: datetime

    def create_authority_tree(self) -> AuthorityRootNode:
        owner = RoleSignature.create_filled_role_signature(self.name, "owner", self.owner_lut)
        active = RoleSignature.create_filled_role_signature(self.name, "active", self.active_lut)
        posting = RoleSignature.create_filled_role_signature(self.name, "posting", self.posting_lut)
        return AuthorityRootNode(owner=owner, active=active, posting=posting)
