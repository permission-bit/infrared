import subprocess
import shutil
import platform

def get_os():
    system = platform.system().lower()
    if system == "darwin":
        system = "macos"
        return system

def is_installed(tool: str) -> bool:
    return shutil.which(tool) is not None

def run(command: list[str]):
    return subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=True
    )

def repository():

    if is_installed("brew"):
        print("brew is installed")
    else:
        if get_os() == "macos":
            try:
                run([""])


    if is_installed("git"):
        print("git is installed")
    else:
        if get_os() == "macos":
            try:
                run(["brew", "install", "git"])
            except Exception as e:
                print(e)