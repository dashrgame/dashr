from typing import Any
import json
import os


def load_settings() -> dict[str, Any]:
    current_dir = os.path.dirname(__file__)
    default_settings_path = os.path.join(current_dir, "..", "default.json")

    with open(default_settings_path, "r") as f:
        default_settings = json.load(f)

    user_settings_path = os.path.expanduser("~/dashr/user_settings.json")

    with open(user_settings_path, "r") as f:
        user_settings = json.load(f)

    settings = default_settings.copy()
    for key in default_settings:
        if key in user_settings:
            settings[key] = user_settings[key]
    return settings


def save_settings(settings: dict[str, Any]) -> None:
    user_settings_path = os.path.expanduser("~/dashr/user_settings.json")
    with open(user_settings_path, "w") as f:
        json.dump(settings, f, indent=4)
