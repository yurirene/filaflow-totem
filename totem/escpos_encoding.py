import re
import unicodedata
from typing import Final

# WPC1252 — compatível com a maioria das térmicas ESC/POS no Brasil (Windows Latin-1)
PRINTER_ENCODING: Final[str] = "cp1252"
# ESC t n — tabela de caracteres Epson (16 = WPC1252)
ESC_POS_CODE_PAGE: Final[int] = 16

_EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0000FE00-\U0000FE0F]"
)


def sanitize_text(text: str) -> str:
    """Remove emojis e normaliza texto para impressoras térmicas."""
    if not text:
        return ""

    cleaned = _EMOJI_RE.sub("", str(text))
    cleaned = cleaned.replace("\u2014", "-").replace("\u2013", "-")
    cleaned = cleaned.replace("\u00a0", " ")
    return " ".join(cleaned.split())


def escpos_select_codepage() -> bytes:
    return b"\x1b\x74" + bytes([ESC_POS_CODE_PAGE])


def encode_printer_text(text: str) -> bytes:
    """Codifica texto no charset da impressora térmica."""
    sanitized = sanitize_text(text)
    try:
        return sanitized.encode(PRINTER_ENCODING)
    except UnicodeEncodeError:
        normalized = unicodedata.normalize("NFKD", sanitized)
        ascii_text = normalized.encode("ascii", errors="ignore").decode("ascii")
        return ascii_text.encode(PRINTER_ENCODING, errors="replace")
