import json
import os
from typing import Optional

from totem.paths import get_config_path


def load_config() -> dict:
    path = get_config_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def get_printer_name() -> Optional[str]:
    printer = load_config().get("printer", "").strip()
    return printer or None
