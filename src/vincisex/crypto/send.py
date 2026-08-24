from .encrypt import SecureFileCryptoStream
from .read_keys import get_cwd_public_key
from .write_keys import cwd_keys

from pathlib import Path
import time
import socket
import struct
import zipfile



def create_package(
    files: list[Path]
):

    package = Path.cwd() / "package.zip"


    with zipfile.ZipFile(
        package,
        "w"
    ) as z:

        for file in files:

            if not file.exists():

                raise FileNotFoundError(
                    f"File not found: {file}"
                )


            z.write(
                file,
                arcname=file.name
            )


            print(
                f"Added: {file}"
            )


    return package



def send_file(
    ip: str,
    port: int,
    file: Path
):

    file_size = file.stat().st_size


    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as s:


        s.connect(
            (ip, port)
        )


        # Größe senden
        s.sendall(
            struct.pack(
                "!Q",
                file_size
            )
        )


        # Datei senden
        with open(
            file,
            "rb"
        ) as f:


            while chunk := f.read(4096):

                s.sendall(
                    chunk
                )


    print(
        f"Sent: {file}"
    )

    print(
        f"Size: {file_size} bytes"
    )



def encrypt_and_send_files(
    ip: str,
    port: int,
    files: list[Path]
):


    # ZIP erstellen
    package = create_package(
        files
    )


    # Key prüfen
    key_location = (
        Path.cwd() /
        "public_key.pem"
    )


    if not key_location.exists():

        cwd_keys()

        time.sleep(1)



    public_key = get_cwd_public_key()


    crypto = SecureFileCryptoStream(
        public_key=public_key
    )


    # ZIP verschlüsseln
    crypto.encrypt_file(
        package
    )


    encrypted_package = (
        Path.cwd() /
        "package.zip.enc"
    )


    # verschickte Datei
    send_file(
        ip,
        port,
        encrypted_package
    )



"""
encrypt_and_send_files(
    "127.0.0.1",
    4545,
    [
        Path("message.txt"),
        Path("image.png"),
        Path("document.pdf")
    ]
)
"""