import time
import platform
import subprocess
import os
DARK_GREEN = "\033[38;5;28m" 
RESET = "\033[0m"

def maximize_window():
    os.system("cls" if os.name == "nt" else "clear")

    os_name = platform.system()

    if os_name.lower() == "darwin":
        return "macos"


    if os_name == "macos":
        subprocess.run([
            "osascript",
            "-e",
            'tell application "Terminal" to set bounds of front window to {0, 0, 1440, 900}'
        ])
    elif os_name == "linux":
        subprocess.run([
            "gnome-terminal",
            "--maximize",
        ])

def cobra():
    snake = r"""
                                                ░░▒▒▒▒▒▒░░░▒▒▒▒▒▒▒░
                                           ░░▒▒░░▒▒▒▒▒▒░░░▒▒▒▒▒▒▒▒░░░░
                                       ▒▒▒▒▒░ ░░▒▒▒░▓▓▓░░░░▒▓▒░▒▒▒▒▒▒▒▒▓▒░
                                     ▒▒░      ░▓░    ██▓▓▒ ▒▓▒█▓   ▒▒▒▒▒▒▓▓▓▓▓
                                   ▓░        ▒░▒░ ▓░ ▒▒▓▒░▓▒▓░ ▓  ▒░▒       ░▒▓░
                                  ▒░           ░▓  ▒░   ░░▒   ▒░░▒▒            ▒░
                                  ▒               ░ ▒░▒░ ░ ▒░▓▒░░               ▒
                                  ▒                 ░ ░     ░                  ░░
                                   ▒░                ░       ▒   ░            ░░
                                    ▒▒           ░   ▓       ▓  ░            ░
                                      ▒░░            ░                     ░░
                                        ░░░░      ░            ░         ░░
                                            ░▒░    ▒      ░   ░         ░         ░
                                 ░░                 ░   ░▒░   ░   ░░░░            ░░░░▒▒░
                          ░░▒░▒░                     ░   ▓   ▒      ▒▒▒▒░               ░▒░░
                       ░▒▒░                             ░▒░           ░▒▒▒▒░              ░▒▒░
                      ░▒▒░          ░░░▒▒░              ░ ░              ░▒▒▓░░           ░▒▒ ▒
                        ▒▒▒░  ░░▒▓▒▒░░                                      ░▓▓▒         ░▒▒▒  ░
                          ░░▒▒▒░             ░░▒▒░░░░                        ▒▓░░     ░▒▒▒▒░
        ░░▒░░▒░░░▒░▒                     ░▒▒▒▒▒░▒       ░░                   ▒▒▒ ░ ░░▒▒░░░
     ░▒▒░           ░░░                ░▒▒▒▒▒░                              ▒▓▒░ ░
   ▒▒░                  ░             ▒  ░▓▒▒░░                        ░  ░▒▓▒░
  ░▒▒░                               ░    ░▒▒░▒▓░                   ░▒░▒░▒▓▒░
    ░▒▒░                                    ░▒░░▓▒▓▓░░▒▒▒ ▒▒▒▒▒░▒▓▒▒▓▒░▒▒░░
       ░▒▒▒░▒▒░▒░ ▒░░▒░░▒░                      ▒  ▒▒▒░░▓░▒▓░░▓▒░▒░░░  ░                  
                         ░▒▓▒                           ░                                 
                            ░▒▒                                                           
                              ░▒░░░                                                      
                                 ░░░░░░                                             
                                     ░░░
                                   ▒████▓
                                   ▒░░▓ ░░
                                    ░░░░░
                                     ░░░
    """

    for line in snake.splitlines():
        print(DARK_GREEN + line + RESET)
        time.sleep(0.04)