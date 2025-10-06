from os import path
import random


def pick_a_splash_any_splash():
    splashes_file = path.join("client", "assets", "texts", "splashes.txt")

    with open(splashes_file, "r", encoding="utf-8") as f:
        splashes = [
            line.strip()
            for line_num, line in enumerate(f, 1)
            if line.strip() and line_num != 79
        ]

    return random.choice(splashes) if splashes else "Welcome to Dashr!"
