import json
import os
from typing import Optional

from totem.paths import get_config_path

DEFAULT_PAPER_MM = 80
VALID_PAPER_WIDTHS = (58, 80)


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


def get_paper_width_mm() -> int:
    value = load_config().get("paper_width_mm", DEFAULT_PAPER_MM)
    try:
        paper = int(value)
    except (TypeError, ValueError):
        return DEFAULT_PAPER_MM
    if paper in VALID_PAPER_WIDTHS:
        return paper
    return DEFAULT_PAPER_MM
