from pathlib import Path

def file_to_cwd(file_name: str, content: str):
    "Saves the file in the current working directory."
    (Path.cwd() / file_name).write_text(content, encoding="utf-8")


def file_to_library(file_name: str, content: str):
    "Saves the file relative to the location of this library file."
    (Path(__file__).parent / file_name).write_text(content, encoding="utf-8")

"""
file_to_library("text.txt", "hello mom")
"""