from __future__ import annotations

from pathlib import Path
import os
import struct

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    RSAPublicKey,
)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


MAGIC = b"VINCISEX"
VERSION = 1

NONCE_SIZE = 12
AES_KEY_SIZE = 32
GCM_TAG_SIZE = 16
CHUNK_SIZE = 1024 * 1024


class SecureFileCryptoStream:
    """
    RSA + AES-256-GCM file encryption.

    Encryption:
        RSA-OAEP -> protects random AES-256 key
        AES-256-GCM -> encrypts file contents

    Decryption:
        RSA-OAEP -> recovers AES-256 key
        AES-256-GCM -> decrypts and authenticates file contents
    """

    def __init__(
        self,
        public_key: RSAPublicKey | None = None,
        public_key_path: str | Path | None = None,
        private_key: RSAPrivateKey | None = None,
        private_key_path: str | Path | None = None,
    ) -> None:

        self.public_key = None
        self.private_key = None

        # ---------------------------------------------------------
        # Public key
        # ---------------------------------------------------------

        if public_key is not None:
            if not isinstance(public_key, RSAPublicKey):
                raise TypeError(
                    "public_key must be an RSA public key."
                )

            self.public_key = public_key

        elif public_key_path is not None:
            public_key_path = Path(public_key_path)

            if not public_key_path.is_file():
                raise FileNotFoundError(
                    f"Public key not found: {public_key_path}"
                )

            with public_key_path.open("rb") as f:
                key = serialization.load_pem_public_key(
                    f.read()
                )

            if not isinstance(key, RSAPublicKey):
                raise TypeError(
                    "The provided public key must be an RSA public key."
                )

            self.public_key = key

        # ---------------------------------------------------------
        # Private key
        # ---------------------------------------------------------

        if private_key is not None:
            if not isinstance(private_key, RSAPrivateKey):
                raise TypeError(
                    "private_key must be an RSA private key."
                )

            self.private_key = private_key

        elif private_key_path is not None:
            private_key_path = Path(private_key_path)

            if not private_key_path.is_file():
                raise FileNotFoundError(
                    f"Private key not found: {private_key_path}"
                )

            with private_key_path.open("rb") as f:
                key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                )

            if not isinstance(key, RSAPrivateKey):
                raise TypeError(
                    "The provided private key must be an RSA private key."
                )

            self.private_key = key

    # =============================================================
    # ENCRYPT
    # =============================================================

    def encrypt(
        self,
        *paths: str | Path,
    ) -> list[Path]:
        """
        Encrypt one or more files/directories.

        Directories are processed recursively.

        Examples:

            encrypt("file.txt")

            encrypt("file1.txt", "file2.txt")

            encrypt(
                "file.txt",
                "documents/",
                "image.png",
            )
        """

        if self.public_key is None:
            raise ValueError(
                "A public key is required for encryption."
            )

        if not paths:
            raise ValueError(
                "At least one file or directory must be provided."
            )

        encrypted_files: list[Path] = []

        for path in paths:
            path = Path(path)

            if not path.exists():
                raise FileNotFoundError(
                    f"Path not found: {path}"
                )

            if path.is_file():
                encrypted_files.append(
                    self.encrypt_file(path)
                )

            elif path.is_dir():
                encrypted_files.extend(
                    self.encrypt_directory(path)
                )

            else:
                raise ValueError(
                    f"Unsupported path: {path}"
                )

        return encrypted_files

    # -------------------------------------------------------------
    # Encrypt single file
    # -------------------------------------------------------------

    def encrypt_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
    ) -> Path:

        if self.public_key is None:
            raise ValueError(
                "A public key is required for encryption."
            )

        input_path = Path(input_path)

        if not input_path.is_file():
            raise FileNotFoundError(
                f"Input file not found: {input_path}"
            )

        if output_path is None:
            output_path = input_path.with_suffix(
                input_path.suffix + ".enc"
            )
        else:
            output_path = Path(output_path)

        if input_path.resolve() == output_path.resolve():
            raise ValueError(
                "Input and output paths must be different."
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ---------------------------------------------------------
        # Random AES-256 key + GCM nonce
        # ---------------------------------------------------------

        aes_key = os.urandom(AES_KEY_SIZE)
        nonce = os.urandom(NONCE_SIZE)

        # ---------------------------------------------------------
        # Encrypt AES key using RSA-OAEP
        # ---------------------------------------------------------

        encrypted_key = self.public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # ---------------------------------------------------------
        # AES-256-GCM
        # ---------------------------------------------------------

        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(nonce),
        )

        encryptor = cipher.encryptor()

        try:
            with (
                input_path.open("rb") as source,
                output_path.open("wb") as target,
            ):

                # Header
                target.write(MAGIC)
                target.write(
                    struct.pack("B", VERSION)
                )

                target.write(
                    struct.pack(
                        ">I",
                        len(encrypted_key),
                    )
                )

                target.write(encrypted_key)
                target.write(nonce)

                # File data
                while True:
                    chunk = source.read(CHUNK_SIZE)

                    if not chunk:
                        break

                    target.write(
                        encryptor.update(chunk)
                    )

                encryptor.finalize()

                # Authentication tag
                target.write(
                    encryptor.tag
                )

        except Exception:
            try:
                output_path.unlink(missing_ok=True)
            except OSError:
                pass

            raise

        return output_path

    # -------------------------------------------------------------
    # Encrypt directory
    # -------------------------------------------------------------

    def encrypt_directory(
        self,
        directory: str | Path,
    ) -> list[Path]:

        directory = Path(directory)

        if not directory.is_dir():
            raise NotADirectoryError(
                f"Not a directory: {directory}"
            )

        encrypted_files: list[Path] = []

        for path in directory.rglob("*"):

            if not path.is_file():
                continue

            if path.name.endswith(".enc"):
                continue

            encrypted_files.append(
                self.encrypt_file(path)
            )

        return encrypted_files

    # =============================================================
    # DECRYPT
    # =============================================================

    def decrypt(
        self,
        *paths: str | Path,
    ) -> list[Path]:
        """
        Decrypt one or more encrypted files/directories.

        Directories are processed recursively.

        Examples:

            decrypt("file.txt.enc")

            decrypt(
                "file1.txt.enc",
                "file2.pdf.enc",
            )

            decrypt("encrypted_folder/")
        """

        if self.private_key is None:
            raise ValueError(
                "A private key is required for decryption."
            )

        if not paths:
            raise ValueError(
                "At least one file or directory must be provided."
            )

        decrypted_files: list[Path] = []

        for path in paths:
            path = Path(path)

            if not path.exists():
                raise FileNotFoundError(
                    f"Path not found: {path}"
                )

            if path.is_file():
                decrypted_files.append(
                    self.decrypt_file(path)
                )

            elif path.is_dir():
                decrypted_files.extend(
                    self.decrypt_directory(path)
                )

            else:
                raise ValueError(
                    f"Unsupported path: {path}"
                )

        return decrypted_files

    # -------------------------------------------------------------
    # Decrypt single file
    # -------------------------------------------------------------

    def decrypt_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
    ) -> Path:

        if self.private_key is None:
            raise ValueError(
                "A private key is required for decryption."
            )

        input_path = Path(input_path)

        if not input_path.is_file():
            raise FileNotFoundError(
                f"Encrypted file not found: {input_path}"
            )

        if output_path is None:

            if input_path.name.endswith(".enc"):
                output_path = input_path.with_name(
                    input_path.name[:-4]
                )
            else:
                output_path = input_path.with_suffix(
                    input_path.suffix + ".decrypted"
                )

        else:
            output_path = Path(output_path)

        if input_path.resolve() == output_path.resolve():
            raise ValueError(
                "Input and output paths must be different."
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            with input_path.open("rb") as source:

                # -------------------------------------------------
                # Read and validate MAGIC
                # -------------------------------------------------

                magic = source.read(
                    len(MAGIC)
                )

                if magic != MAGIC:
                    raise ValueError(
                        "Invalid VINCISEX file."
                    )

                # -------------------------------------------------
                # Version
                # -------------------------------------------------

                version_data = source.read(1)

                if len(version_data) != 1:
                    raise ValueError(
                        "Invalid or truncated VINCISEX header."
                    )

                version = struct.unpack(
                    "B",
                    version_data,
                )[0]

                if version != VERSION:
                    raise ValueError(
                        f"Unsupported VINCISEX version: {version}"
                    )

                # -------------------------------------------------
                # Encrypted AES key length
                # -------------------------------------------------

                key_length_data = source.read(4)

                if len(key_length_data) != 4:
                    raise ValueError(
                        "Invalid or truncated encrypted key length."
                    )

                encrypted_key_length = struct.unpack(
                    ">I",
                    key_length_data,
                )[0]

                if encrypted_key_length <= 0:
                    raise ValueError(
                        "Invalid encrypted key length."
                    )

                # -------------------------------------------------
                # Encrypted AES key
                # -------------------------------------------------

                encrypted_key = source.read(
                    encrypted_key_length
                )

                if len(encrypted_key) != encrypted_key_length:
                    raise ValueError(
                        "Encrypted AES key is truncated."
                    )

                # -------------------------------------------------
                # Nonce
                # -------------------------------------------------

                nonce = source.read(
                    NONCE_SIZE
                )

                if len(nonce) != NONCE_SIZE:
                    raise ValueError(
                        "Invalid or truncated nonce."
                    )

                # -------------------------------------------------
                # Recover AES key using RSA-OAEP
                # -------------------------------------------------

                aes_key = self.private_key.decrypt(
                    encrypted_key,
                    padding.OAEP(
                        mgf=padding.MGF1(
                            algorithm=hashes.SHA256()
                        ),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )

                if len(aes_key) != AES_KEY_SIZE:
                    raise ValueError(
                        "Invalid AES key."
                    )

                # -------------------------------------------------
                # Determine encrypted payload size
                # -------------------------------------------------

                current_position = source.tell()
                file_size = input_path.stat().st_size

                remaining = (
                    file_size
                    - current_position
                )

                if remaining < GCM_TAG_SIZE:
                    raise ValueError(
                        "Encrypted file is truncated."
                    )

                encrypted_data_size = (
                    remaining - GCM_TAG_SIZE
                )

                # -------------------------------------------------
                # Read GCM authentication tag
                # -------------------------------------------------

                source.seek(
                    file_size - GCM_TAG_SIZE
                )

                tag = source.read(
                    GCM_TAG_SIZE
                )

                # -------------------------------------------------
                # Return to encrypted payload
                # -------------------------------------------------

                source.seek(
                    current_position
                )

                cipher = Cipher(
                    algorithms.AES(aes_key),
                    modes.GCM(
                        nonce,
                        tag,
                    ),
                )

                decryptor = cipher.decryptor()

                # -------------------------------------------------
                # Decrypt into temporary file first
                #
                # This prevents replacing the final output with
                # corrupted/plaintext data if authentication fails.
                # -------------------------------------------------

                temporary_output = output_path.with_name(
                    output_path.name + ".tmp"
                )

                try:

                    with temporary_output.open("wb") as target:

                        remaining_data = encrypted_data_size

                        while remaining_data > 0:

                            chunk_size = min(
                                CHUNK_SIZE,
                                remaining_data,
                            )

                            chunk = source.read(
                                chunk_size
                            )

                            if len(chunk) != chunk_size:
                                raise ValueError(
                                    "Encrypted file is truncated."
                                )

                            target.write(
                                decryptor.update(chunk)
                            )

                            remaining_data -= len(chunk)

                        # -------------------------------------------------
                        # Authentication check
                        # -------------------------------------------------

                        target.write(
                            decryptor.finalize()
                        )

                    # Only move into place after successful
                    # AES-GCM authentication.
                    temporary_output.replace(
                        output_path
                    )

                except Exception:
                    try:
                        temporary_output.unlink(
                            missing_ok=True
                        )
                    except OSError:
                        pass

                    raise

        except Exception:
            raise

        return output_path

    # -------------------------------------------------------------
    # Decrypt directory
    # -------------------------------------------------------------

    def decrypt_directory(
        self,
        directory: str | Path,
    ) -> list[Path]:

        directory = Path(directory)

        if not directory.is_dir():
            raise NotADirectoryError(
                f"Not a directory: {directory}"
            )

        decrypted_files: list[Path] = []

        for path in directory.rglob("*"):

            if not path.is_file():
                continue

            # Only process VINCISEX encrypted files.
            if not path.name.endswith(".enc"):
                continue

            decrypted_files.append(
                self.decrypt_file(path)
            )

        return decrypted_files


"""
USAGE
=====

BASIC SETUP
-----------

from infraredx import SecureFileCryptoStream
from infraredx import get_cwd_public_key

public_key = get_cwd_public_key(
    "crypto/public_key.pem"
)

crypto = SecureFileCryptoStream(
    public_key=public_key
)


ENCRYPT
=======

SINGLE FILE
-----------

crypto.encrypt("document.pdf")


MULTIPLE FILES
--------------

crypto.encrypt(
    "file1.pdf",
    "file2.jpg",
    "file3.txt",
)


FOLDER (RECURSIVE)
------------------

crypto.encrypt("Documents")


MIXED FILES AND FOLDERS
-----------------------

crypto.encrypt(
    "document.pdf",
    "Pictures",
    "backup.zip",
    "Projects",
)


DIRECT FILE ENCRYPTION
----------------------

crypto.encrypt_file(
    "document.pdf"
)


FILE WITH CUSTOM OUTPUT PATH
----------------------------

crypto.encrypt_file(
    "document.pdf",
    "encrypted/document.dat"
)


DECRYPT
=======

For decryption, a private RSA key is required.

from infraredx import SecureFileCryptoStream
from infraredx import get_cwd_private_key

private_key = get_cwd_private_key(
    "crypto/private_key.pem"
)

crypto = SecureFileCryptoStream(
    private_key=private_key
)


SINGLE FILE
-----------

crypto.decrypt(
    "document.pdf.enc"
)


MULTIPLE FILES
--------------

crypto.decrypt(
    "file1.pdf.enc",
    "file2.jpg.enc",
    "file3.txt.enc",
)


FOLDER (RECURSIVE)
------------------

crypto.decrypt(
    "Documents"
)


MIXED FILES AND FOLDERS
-----------------------

crypto.decrypt(
    "document.pdf.enc",
    "Pictures",
    "backup.zip.enc",
    "Projects",
)


DIRECT FILE DECRYPTION
----------------------

crypto.decrypt_file(
    "document.pdf.enc"
)


FILE WITH CUSTOM OUTPUT PATH
----------------------------

crypto.decrypt_file(
    "document.pdf.enc",
    "decrypted/document.pdf"
)


ENCRYPT AND DECRYPT
===================

Encrypt:

crypto.encrypt(
    "document.pdf"
)

Result:

document.pdf.enc


Decrypt:

crypto.decrypt(
    "document.pdf.enc"
)

Result:

document.pdf


MULTIPLE DIRECTORIES
====================

crypto.encrypt(
    "Documents",
    "Pictures",
    "Projects",
)


RESULT
======

All methods return a list of generated files when using
encrypt() or decrypt().

Example:

encrypted = crypto.encrypt(
    "Documents",
    "file.pdf"
)

for file in encrypted:
    print(file)


decrypted = crypto.decrypt(
    "Documents"
)

for file in decrypted:
    print(file)
"""