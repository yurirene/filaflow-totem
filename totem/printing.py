import json
import os
import sys
import tempfile
from typing import Optional

from totem.escpos_encoding import (
    PRINTER_ENCODING,
    encode_printer_text,
    escpos_select_codepage,
    sanitize_text,
)

IS_WINDOWS = sys.platform == "win32"

# Largura útil em caracteres (fonte padrão ESC/POS)
PAPER_CHAR_WIDTH = {
    58: 32,
    80: 48,
}

DEFAULT_PAPER_MM = 80


def normalize_paper_width(paper_mm: Optional[int]) -> int:
    if paper_mm in PAPER_CHAR_WIDTH:
        return paper_mm
    return DEFAULT_PAPER_MM


def get_char_width(paper_mm: Optional[int]) -> int:
    return PAPER_CHAR_WIDTH[normalize_paper_width(paper_mm)]


def list_printers() -> list[str]:
    if IS_WINDOWS:
        import win32print

        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return [printer[2] for printer in win32print.EnumPrinters(flags)]

    import cups

    conn = cups.Connection()
    return list(conn.getPrinters().keys())


def _center(text: str, width: int) -> str:
    text = text.strip()
    if len(text) > width:
        return text[:width]
    return text.center(width)


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _big_codigo_lines(codigo: str, width: int) -> list[str]:
    """Número da senha em destaque (fallback texto plano)."""
    codigo = codigo.strip().upper()
    if not codigo:
        return []

    spaced = " ".join(list(codigo))
    border = "=" * width

    lines = ["", border, ""]
    for _ in range(3):
        lines.append(_center(spaced, width))
        lines.append("")
    lines.extend([border, ""])
    return lines


def format_thermal_ticket(data: dict, paper_mm: Optional[int] = None) -> str:
    width = get_char_width(paper_mm)
    clinica = sanitize_text(data.get("clinica", ""))
    codigo = sanitize_text(data.get("codigo", ""))
    servico = sanitize_text(data.get("servico", ""))
    badge = sanitize_text(data.get("badge", ""))
    data_hora = sanitize_text(data.get("data", ""))
    espera = data.get("espera", 0)
    posicao = data.get("posicao", 1)

    lines: list[str] = []
    lines.append("=" * width)
    lines.extend(_wrap(clinica, width))
    if data_hora:
        lines.append(_center(data_hora, width))
    lines.append("=" * width)
    lines.append("")

    if badge:
        lines.extend(_wrap(badge, width))
        lines.append("")

    lines.extend(_big_codigo_lines(codigo, width))

    if servico:
        lines.extend(_wrap(servico, width))
        lines.append("")

    lines.append(_center(f"Espera: ~{espera} min", width))
    lines.append(_center(f"Posição: {posicao}", width))
    lines.append("")
    lines.extend(_wrap("Aguarde ser chamado no painel", width))
    lines.append("")
    lines.append("=" * width)
    lines.append("")
    return "\n".join(lines)


def _escpos_init() -> bytes:
    return b"\x1b\x40" + escpos_select_codepage()


def _escpos_align(mode: int) -> bytes:
    return b"\x1b\x61" + bytes([mode])


def _escpos_size(normal: bool = True, double_height: bool = False, double_width: bool = False) -> bytes:
    mode = 0
    if double_height:
        mode |= 0x10
    if double_width:
        mode |= 0x20
    if not normal and not mode:
        mode = 0x30
    return b"\x1b\x21" + bytes([mode])


def _escpos_gs_size(width_mul: int = 1, height_mul: int = 1) -> bytes:
    width_mul = max(1, min(width_mul, 8))
    height_mul = max(1, min(height_mul, 8))
    value = ((height_mul - 1) << 4) | (width_mul - 1)
    return b"\x1d\x21" + bytes([value])


def _escpos_cut() -> bytes:
    return b"\x1d\x56\x00"


def _escpos_text(text: str) -> bytes:
    return encode_printer_text(text)


def _escpos_codigo_block(codigo: str, width_mul: int, height_mul: int, repeats: int = 2) -> bytes:
    parts: list[bytes] = [_escpos_text("\n")]
    for _ in range(repeats):
        parts.append(_escpos_gs_size(width_mul, height_mul))
        parts.append(_escpos_text(codigo + "\n\n"))
    parts.append(_escpos_gs_size(1, 1))
    return b"".join(parts)


def build_escpos_ticket(data: dict, paper_mm: Optional[int] = None) -> bytes:
    width = get_char_width(paper_mm)
    paper = normalize_paper_width(paper_mm)
    clinica = sanitize_text(data.get("clinica", ""))
    codigo = sanitize_text(str(data.get("codigo", ""))).strip().upper()
    servico = sanitize_text(data.get("servico", ""))
    badge = sanitize_text(data.get("badge", ""))
    data_hora = sanitize_text(data.get("data", ""))
    espera = data.get("espera", 0)
    posicao = data.get("posicao", 1)

    # 80mm: 4x — 58mm: 3x (máximo que cabe confortavelmente na bobina)
    codigo_w, codigo_h = (4, 4) if paper == 80 else (3, 3)
    codigo_repeats = 3 if paper == 80 else 2

    parts: list[bytes] = [_escpos_init(), _escpos_align(1)]

    parts.append(_escpos_text("=" * width + "\n"))
    for line in _wrap(clinica, width):
        parts.append(_escpos_size(double_height=True) + _escpos_text(line + "\n"))
    parts.append(_escpos_size())
    if data_hora:
        parts.append(_escpos_text(data_hora + "\n"))
    parts.append(_escpos_text("=" * width + "\n\n"))

    if badge:
        parts.append(_escpos_size(double_width=True) + _escpos_text(badge + "\n"))
        parts.append(_escpos_size() + _escpos_text("\n"))

    parts.append(_escpos_codigo_block(codigo, codigo_w, codigo_h, codigo_repeats))

    if servico:
        parts.append(_escpos_size(double_width=True) + _escpos_text(servico + "\n"))
        parts.append(_escpos_size() + _escpos_text("\n"))

    parts.append(_escpos_text(f"Espera: ~{espera} min\n"))
    parts.append(_escpos_text(f"Posição: {posicao}\n\n"))
    for line in _wrap("Aguarde ser chamado no painel", width):
        parts.append(_escpos_text(line + "\n"))
    parts.append(_escpos_text("\n" + "=" * width + "\n\n"))
    parts.append(_escpos_cut())
    return b"".join(parts)


def _print_raw(printer_name: str, payload: bytes) -> None:
    if IS_WINDOWS:
        import win32print

        handle = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(handle, 1, ("Senha Totem", None, "RAW"))
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, payload)
            win32print.EndPagePrinter(handle)
            win32print.EndDocPrinter(handle)
        finally:
            win32print.ClosePrinter(handle)
        return

    import cups

    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
        tmp.write(payload)
        temp_path = tmp.name

    try:
        conn = cups.Connection()
        conn.printFile(
            printer_name,
            temp_path,
            "Senha Totem",
            {"document-format": "application/octet-stream"},
        )
    finally:
        os.remove(temp_path)


def print_ticket(
    printer_name: str,
    ticket_data: dict,
    work_dir: str,
    paper_mm: Optional[int] = None,
) -> None:
    paper = normalize_paper_width(paper_mm)
    payload = build_escpos_ticket(ticket_data, paper)
    try:
        _print_raw(printer_name, payload)
    except Exception:
        content = format_thermal_ticket(ticket_data, paper)
        print_test_file(printer_name, content, work_dir)


def print_test_file(printer_name: str, content: str, work_dir: str) -> None:
    test_file = os.path.join(work_dir, "teste_impressao.txt")
    with open(test_file, "w", encoding=PRINTER_ENCODING, errors="replace") as f:
        f.write(content)

    if IS_WINDOWS:
        import win32api

        win32api.ShellExecute(0, "print", test_file, f'/d:"{printer_name}"', ".", 0)
    else:
        import cups

        conn = cups.Connection()
        conn.printFile(printer_name, test_file, "Teste Totem", {})


def sample_ticket_data() -> dict:
    return {
        "clinica": "Clínica Filaflow",
        "codigo": "T001",
        "servico": "Triagem",
        "badge": "Atendimento Normal",
        "data": "09/06/2025 21:00",
        "espera": 5,
        "posicao": 2,
    }
