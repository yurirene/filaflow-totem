import os
import sys
import tempfile

IS_WINDOWS = sys.platform == "win32"
THERMAL_WIDTH = 32


def list_printers() -> list[str]:
    if IS_WINDOWS:
        import win32print

        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return [printer[2] for printer in win32print.EnumPrinters(flags)]

    import cups

    conn = cups.Connection()
    return list(conn.getPrinters().keys())


def _center(text: str, width: int = THERMAL_WIDTH) -> str:
    text = text.strip()
    if len(text) > width:
        return text[:width]
    return text.center(width)


def _wrap(text: str, width: int = THERMAL_WIDTH) -> list[str]:
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


def format_thermal_ticket(data: dict, width: int = THERMAL_WIDTH) -> str:
    clinica = data.get("clinica", "")
    codigo = data.get("codigo", "")
    servico = data.get("servico", "")
    badge = data.get("badge", "")
    data_hora = data.get("data", "")
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

    lines.append(_center(codigo, width))
    lines.append("")

    if servico:
        lines.extend(_wrap(servico, width))
        lines.append("")

    lines.append(f"Espera: ~{espera} min")
    lines.append(f"Posicao: {posicao}")
    lines.append("")
    lines.extend(_wrap("Aguarde ser chamado no painel", width))
    lines.append("")
    lines.append("=" * width)
    lines.append("")
    return "\n".join(lines)


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


def print_ticket(printer_name: str, ticket_data: dict, work_dir: str) -> None:
    content = format_thermal_ticket(ticket_data)
    payload = content.encode("utf-8", errors="replace") + b"\n\n\x1d\x56\x00"
    try:
        _print_raw(printer_name, payload)
    except Exception:
        print_test_file(printer_name, content, work_dir)


def print_test_file(printer_name: str, content: str, work_dir: str) -> None:
    test_file = os.path.join(work_dir, "teste_impressao.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(content)

    if IS_WINDOWS:
        import win32api

        win32api.ShellExecute(0, "print", test_file, f'/d:"{printer_name}"', ".", 0)
    else:
        import cups

        conn = cups.Connection()
        conn.printFile(printer_name, test_file, "Teste Totem", {})
