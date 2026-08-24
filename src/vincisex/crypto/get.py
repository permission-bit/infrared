from .encrypt import SecureFileCryptoStream
from .read_keys import get_cwd_private_key

from pathlib import Path
import socket
import struct
import zipfile
import os



def receive_file(conn):

    header = b""


    while len(header) < 8:

        chunk = conn.recv(
            8 - len(header)
        )

        if not chunk:

            raise ConnectionError(
                "Connection aborted during header"
            )

        header += chunk


    file_size = struct.unpack(
        "!Q",
        header
    )[0]


    print(
        f"Expecting encrypted package: {file_size} bytes"
    )


    received = 0

    encrypted_file = Path.cwd() / "package.zip.enc"


    with open(
        encrypted_file,
        "wb"
    ) as f:

        while received < file_size:

            chunk = conn.recv(
                min(
                    4096,
                    file_size - received
                )
            )

            if not chunk:

                raise ConnectionError(
                    "Connection interrupted"
                )


            f.write(chunk)

            received += len(chunk)


    print(
        f"Received: {received} bytes"
    )


    return encrypted_file



def listen(
    ip: str,
    port: int
):

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server:


        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )


        server.bind(
            (ip, port)
        )


        server.listen(5)


        print(
            f"Server running on {ip}:{port}"
        )


        conn, addr = server.accept()


        print(
            f"Connection from {addr}"
        )


        with conn:

            return receive_file(conn)



def decrypt_and_extract():

    private_key_location = (
        Path.cwd() /
        "private_key.pem"
    )


    if not private_key_location.exists():

        print(
            f"Missing key: {private_key_location}"
        )

        return



    private_key = get_cwd_private_key()


    crypto = SecureFileCryptoStream(
        private_key=private_key
    )


    encrypted_package = (
        Path.cwd() /
        "package.zip.enc"
    )


    # entschlüsseln
    crypto.decrypt_file(
        encrypted_package
    )


    package = (
        Path.cwd() /
        "package.zip"
    )


    output = (
        Path.cwd() /
        "received"
    )


    output.mkdir(
        exist_ok=True
    )


    with zipfile.ZipFile(
        package,
        "r"
    ) as z:

        for member in z.infolist():

            target_path = output / member.filename

            # verhindert ../ Angriffe
            if not str(target_path.resolve()).startswith(
                str(output.resolve())
            ):
                raise Exception(
                    f"Unsafe file path detected: {member.filename}"
                )


            z.extract(
                member,
                output
            )


            print(
                f"Extracted: {member.filename}"
            )


    print(
        f"Extracted to: {output}"
    )



def listen_receive_decrypt(
    ip: str,
    port: int
):

    listen(
        ip,
        port
    )

    decrypt_and_extract()



"""
listen_receive_decrypt(
    "127.0.0.1",
    4545
)
"""