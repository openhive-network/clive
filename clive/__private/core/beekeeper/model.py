from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel


class BeekeeperResponse(BaseModel):
    pass


class Create(BeekeeperResponse):
    password: str


class CreateKey(BeekeeperResponse):
    public_key: str


class ListWallets(BeekeeperResponse):
    keys: dict[str, str]


class ListKeys(BeekeeperResponse):
    wallets: list[str]


class GetPublicKeys(BeekeeperResponse):
    keys: list[str]


class SignDigest(BeekeeperResponse):
    signature: str


T = TypeVar("T", Create, CreateKey, ListWallets, ListKeys, GetPublicKeys, SignDigest, None)


class HiveResponse(BaseModel, Generic[T]):
    id: Any  # noqa: A003
    jsonrpc: str
    result: T
    error: dict[str, Any] | None = None
