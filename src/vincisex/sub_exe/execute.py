import platform
import shutil
import subprocess
from pathlib import Path


def get_os():
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
        text=True
    )


def find_brew() -> str | None:
    brew = shutil.which("brew")

    if brew:
        return brew

    for path in (
        "/opt/homebrew/bin/brew",  # Apple Silicon
        "/usr/local/bin/brew",     # Intel Mac
    ):
        if Path(path).exists():
            return path

    return None


def install_homebrew() -> str:
    brew = find_brew()

    if brew:
        print("Homebrew ist bereits installiert.")
        return brew

    print("Installiere Homebrew...")

    run([
        "/bin/bash",
        "-c",
        "curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | /bin/bash"
    ])

    brew = find_brew()

    if not brew:
        raise RuntimeError(
            "Homebrew wurde installiert, aber 'brew' wurde nicht gefunden."
        )

    return brew


def install_package(brew: str, package: str):
    if is_installed(package):
        print(f"{package} ist bereits installiert.")
        return

    print(f"Installiere {package}...")

    run([
        brew,
        "install",
        package
    ])


def repository(repsitory_name:str, username:str):
    if get_os() != "macos":
        print("Dieses Setup unterstützt aktuell nur macOS.")
        return

    brew = install_homebrew()

    print("Homebrew:", brew)

    run([
        brew,
        "--version"
    ])

    try:
        install_package(brew, "git")
    except Exception as e:
        print(f"[*] ERROR: {e}")

    if is_installed("git"):
        try:
            run([])



if __name__ == "__main__":
    repository()