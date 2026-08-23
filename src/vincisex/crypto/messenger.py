from vincisex import SecureFileCryptoStream, get_cwd_public_key, cwd_keys, file_to_cwd
from pathlib import Path
import time
import socket
import struct

MESSAGE = (
"""
Hello mom
"""
)

def create_encrypt_send_message(ip:str, port:int, message:str):
    message_dir =  Path.cwd()/"message.txt"

    file_to_cwd("message.txt", message)

    key_location = Path.cwd()/"public_key.pem"

    if key_location.exists():
        print(f"Key: {key_location} exist")
    else:
        cwd_keys()

    time.sleep(1)

    public_key = get_cwd_public_key()

    crypto = SecureFileCryptoStream(
        public_key=public_key
    )

    if message_dir.exists():

        crypto.encrypt_file(message_dir)


    #send 

    encrypted_message_dir = Path.cwd()/"message.enc"

    file_size = encrypted_message_dir.stat().st_size   

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))

        s.sendall(struct.pack("!Q", file_size))

        with open(encrypted_message_dir, "rb") as f:
            while chunk := f.read(4096):
                s.sendall(chunk)

    print(f"Sent: {encrypted_message_dir}")
    print(f"Size: {file_size} bytes")




def receive_file(conn):

    header = b""

    while len(header) < 8:
        chunk = conn.recv(8 - len(header))

        if not chunk:
            raise ConnectionError("Connection was aborted during header exchange")

        header += chunk

    file_size = struct.unpack("!Q", header)[0]

    print(f"Expecting {file_size} bytes")

    received = 0

    received_message_dir =  Path.cwd()/"message.txt"

    with open(received_message_dir, "wb") as f:
        while received < file_size:
            chunk = conn.recv(
                min(4096, file_size - received)
            )

            if not chunk:
                raise ConnectionError(
                    "Connection interrupted during file-transfer"
                    
                )

            f.write(chunk)
            received += len(chunk)

    print(f"Datei vollständig empfangen: {received} Bytes")
    return conn

def listen(ip:str, port:int):
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

            server.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            server.bind((ip, port))
            server.listen(5)

            print(f"Server is running on {ip}:{port}")

            while True:
                conn, addr = server.accept()

                print(f"Verbindung von {addr}")

                with conn:
                    receive_file(conn)
    except Exception:
        quit

def decrypt_received_message():
    private_key_location = Path.cwd()/"private_key.pem"

    if private_key_location.exists():

        private_key = get_cwd_public_key()
        received_message_dir =  Path.cwd()/"message.txt"

        crypto = SecureFileCryptoStream(
            privatec_key=private_key
        )

        crypto.decrypt_file(
            received_message_dir
        )

    else:
        print(f"Your private key direction should be: {private_key_location}")


def listen_receive_decrypt(ip:str, port:int):
    listen(ip, port)
    time.sleep(2)
    decrypt_received_message()
