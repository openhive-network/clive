from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters import argument_related_options
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleValue
from clive.__private.cli.common.parameters.styling import stylized_help

crypto = CliveTyper(name="crypto", help="Commands for cryptographic operations (encryption and decryption).")


_encoded_text_argument = typer.Argument(
    None,
    help=stylized_help("The encoded text to decrypt (starts with '#').", required_as_arg_or_option=True),
)


@crypto.command(name="decrypt")
async def decrypt_memo(
    encoded_text: str | None = _encoded_text_argument,
    encoded_text_option: str | None = argument_related_options.encoded_text,
) -> None:
    """
    Decrypt an encrypted memo.

    Memo is encrypted using the memo keys of sender and receiver of operation. You must have one of
    those private keys in wallet to encrypt/decrypt memo. Other key is public.

    Example:
        clive crypto decrypt "#encoded_text_string"
        clive crypto decrypt --encoded-text "#encoded_text_string"
    """
    from clive.__private.cli.commands.crypto.decrypt import Decrypt  # noqa: PLC0415

    await Decrypt(encrypted_memo=EnsureSingleValue("encoded-text").of(encoded_text, encoded_text_option)).run()
