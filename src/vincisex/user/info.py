import time
import socket
import platform
import getpass
import urllib.request


def get_public_ip():

    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=3) as response:
            return response.read().decode()
    except Exception:
        return "offline"


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def mydata():
    username = getpass.getuser()
    hostname = socket.gethostname()
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    system = platform.system()
    release = platform.release()
    machine = platform.machine()

    local_ip = get_local_ip()
    public_ip = get_public_ip()

    data = (
        f"{username}_"
        f"{hostname}_"
        f"{system}-{release}_"
        f"{machine}_"
        f"LAN-{local_ip}_"
        f"WAN-{public_ip}_"
        f"{timestamp}.tar.gz"
    )

    return data