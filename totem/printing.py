import os
import sys

IS_WINDOWS = sys.platform == "win32"


def list_printers() -> list[str]:
    if IS_WINDOWS:
        import win32print

        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return [printer[2] for printer in win32print.EnumPrinters(flags)]

    import cups

    conn = cups.Connection()
    return list(conn.getPrinters().keys())


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
