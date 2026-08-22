from __future__ import annotations

from pathlib import Path
import os
import struct

from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


current_path = Path.cwd()
CURRENT_PUBLIC_KEY_PATH = current_path/f"public_key.pem"
CURRENT_PRIVATE_KEY_PATH = current_path/f"private_key.pem"

neighbor_path = Path(__file__).resolve().parent
NEIGHBOR_PUBLIC_KEY_PATH = neighbor_path/f"public_key.pem"
NEIGHBOR_PRIVATE_KEY_PATH = neighbor_path/f"private_key.pem"

def get_cwd_public_key():

    PUBLIC_KEY_PATH = CURRENT_PUBLIC_KEY_PATH

    with open(PUBLIC_KEY_PATH, "rb") as f:
        key = serialization.load_pem_public_key(
            f.read()
        )
        return key
    


def get_cwd_private_key():

    PRIVATE_KEY_PATH = CURRENT_PRIVATE_KEY_PATH

    with open(PRIVATE_KEY_PATH, "rb") as f:
        key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
        return key
    


#----------------------------

def get_neighbor_public_key():

    PUBLIC_KEY_PATH = NEIGHBOR_PUBLIC_KEY_PATH

    with open(PUBLIC_KEY_PATH, "rb") as f:
        key = serialization.load_pem_public_key(
            f.read()
        )
        return key
    


def get_neighbor_private_key():

    PRIVATE_KEY_PATH = NEIGHBOR_PRIVATE_KEY_PATH

    with open(PRIVATE_KEY_PATH, "rb") as f:
        key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
        return key
    


#----------------------------

def get_specific_public_key(path):

    with open(path, "rb") as f:
        key = serialization.load_pem_public_key(
            f.read()
        )
        return key
    


def get_specific_private_key(path):

    with open(path, "rb") as f:
        key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
        return key
    

    

