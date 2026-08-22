from __future__ import annotations

from pathlib import Path
import os
import struct

from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from infrared import get_cwd_public_key


MAGIC = b"INFRARED"
VERSION = 1
NONCE_SIZE = 12
CHUNK_SIZE = 1024 * 1024

from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


class SecureFileCryptoStream:
    def __init__(
        self,
        public_key: RSAPublicKey | None = None,
        public_key_path: str | Path | None = None,
    ) -> None:

        if public_key is not None:
            self.public_key = public_key

        elif public_key_path is not None:
            public_key_path = Path(public_key_path)

            with public_key_path.open("rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read()
                )

        else:
            raise ValueError(
                "Either public_key or public_key_path must be provided."
            )



# crypto = SecureFileCryptoStream(
#     public_key_path="crypto/public_key.pem"
# )

# key = get_cwd_public_key("crypto/public_key.pem")

# crypto = SecureFileCryptoStream(
#     public_key=key
# )


# crypto.encrypt_file(
#     "/home/user/Documents/file.pdf",
#     "/home/user/Documents/file.pdf.enc"
# )