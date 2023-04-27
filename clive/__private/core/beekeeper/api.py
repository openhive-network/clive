from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar, get_type_hints

from clive.__private.core.beekeeper.model import (
    Create,  # noqa: TCH001
    CreateKey,  # noqa: TCH001
    EmptyResponse,  # noqa: TCH001
    GetInfo,  # noqa: TCH001
    GetPublicKeys,  # noqa: TCH001
    ImportKey,  # noqa: TCH001
    ListKeys,  # noqa: TCH001
    ListWallets,  # noqa: TCH001
    SignDigest,  # noqa: TCH001
)

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import BeekeeperRemote

FooT = TypeVar("FooT", bound=Callable[..., object])


def api(foo: FooT) -> FooT:
    @wraps(foo)
    def impl(this: BeekeeperApi, **kwargs: Any) -> Any:
        return this._owner._send(
            response=get_type_hints(foo)["return"],
            endpoint=f"beekeeper_api.{foo.__name__}",
            **kwargs,
        ).result

    return impl  # type: ignore


class BeekeeperApi:
    def __init__(self, owner: BeekeeperRemote) -> None:
        self._owner = owner

    @api
    def create(self, *, wallet_name: str, password: str | None = None) -> Create:
        raise NotImplementedError()

    @api
    def open(self, *, wallet_name: str) -> EmptyResponse:  # noqa: A003
        raise NotImplementedError()

    @api
    def set_timeout(self, *, seconds: int) -> EmptyResponse:
        raise NotImplementedError()

    @api
    def lock_all(self) -> EmptyResponse:
        raise NotImplementedError()

    @api
    def lock(self, *, wallet_name: str) -> EmptyResponse:
        raise NotImplementedError()

    @api
    def unlock(self, *, wallet_name: str, password: str) -> EmptyResponse:
        raise NotImplementedError()

    @api
    def import_key(self, *, wallet_name: str, wif_key: str) -> ImportKey:
        raise NotImplementedError()

    @api
    def remove_key(self, *, wallet_name: str, password: str, public_key: str) -> EmptyResponse:
        raise NotImplementedError()

    @api
    def create_key(self, *, wallet_name: str) -> CreateKey:
        raise NotImplementedError()

    @api
    def list_wallets(self) -> ListWallets:
        raise NotImplementedError()

    @api
    def list_keys(self, *, wallet_name: str, password: str) -> ListKeys:
        raise NotImplementedError()

    @api
    def get_public_keys(self) -> GetPublicKeys:
        raise NotImplementedError()

    @api
    def sign_digest(self, *, digest: str, public_key: str) -> SignDigest:
        raise NotImplementedError()

    @api
    def get_info(self) -> GetInfo:
        raise NotImplementedError()
