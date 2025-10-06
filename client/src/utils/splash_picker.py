from os import path
import random
from typing import Optional

splashes_file = path.join("client", "assets", "texts", "splashes.txt")


def pick_a_splash_any_splash():
    with open(splashes_file, "r", encoding="utf-8") as f:
        splashes = [
            line.strip()
            for line_num, line in enumerate(f, 1)
            if line.strip() and line_num != 79
        ]

    return random.choice(splashes) if splashes else "Welcome to Dashr!"


def get_specific_splash(index: int) -> Optional[str]:
    with open(splashes_file, "r", encoding="utf-8") as f:
        splashes = [line.strip() for line_num, line in enumerate(f, 1) if line.strip()]

    if index >= 1 and index <= len(splashes):
        if index == 79:
            return None

        return splashes[index - 1]
    else:
        return "404: Splash Not Found"
