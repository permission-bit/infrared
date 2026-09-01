import platform
import shutil
import subprocess

def get_os() -> str:
    system = platform.system().lower()

    if system == "darwin":
        return "macos"

    if system == "linux":
        return "linux"

    if system == "windows":
        return "windows"

    return system

def is_installed(tool: str) -> bool:
    return shutil.which(tool) is not None


def run(command: list[str]):
    print("$", " ".join(command))

    return subprocess.run(
        command,
        check=True,
        text=True,
    )


def run_capture(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=True,
    )