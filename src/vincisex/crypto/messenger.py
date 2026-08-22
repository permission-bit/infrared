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




