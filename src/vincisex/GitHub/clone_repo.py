from sub_exe import run
import os
import shutil
import subprocess
from pathlib import Path
import sys





def find_python_versions():
    versions = []

    commands = [
        "python",
        "python3",
        "python3.10",
        "python3.11",
        "python3.12",
        "python3.13",
        "python3.14"
    ]

    for command in commands:
        path = shutil.which(command)

        if path:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True
            )

            version = result.stdout.strip().split()[-1]

            versions.append((version, path))

    return versions


def get_highest_python():
    versions = find_python_versions()

    if not versions:
        return None

    versions.sort(
        key=lambda x: tuple(map(int, x[0].split("."))),
        reverse=True
    )

    return versions[0][1]


class Clone:

    def __init__(self, user_name, repository_name):
        self.user_name = user_name
        self.repository_name = repository_name

    def clone_python_repository(self):

        # Repository klonen
        run([
            "git",
            "clone",
            f"https://github.com/{self.user_name}/{self.repository_name}.git"
        ])

        # In Repository wechseln
        os.chdir(self.repository_name)

        # Höchste Python-Version finden
        highest_python = get_highest_python()

        if highest_python is None:
            raise RuntimeError("Keine Python-Version gefunden.")

        print(f"Benutze Python: {highest_python}")


        run([
            highest_python,
            "-m",
            "venv",
            "venv"
        ])

        if Path("requirements.txt").exists():

            run([
                "./venv/bin/python",
                "-m",
                "pip",
                "install",
                "-r",
                "requirements.txt"
            ])

        else:
            sys.exit()


"""
repo = Clone("permission-bit", "infrared")

repo.clone_python_repository()
"""