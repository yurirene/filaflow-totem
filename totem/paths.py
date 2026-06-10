import os
import sys


def get_app_dir() -> str:
    """Diretório onde config.json e arquivos persistentes devem ficar."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_path() -> str:
    return os.path.join(get_app_dir(), "config.json")
