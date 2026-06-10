import json

from PyQt6.QtCore import QObject, pyqtSlot

from totem.config_store import get_printer_name
from totem.paths import get_app_dir
from totem.printing import print_ticket


class TotemBridge(QObject):
    @pyqtSlot(str, result=bool)
    def printTicket(self, payload: str) -> bool:
        try:
            data = json.loads(payload)
            printer = get_printer_name()
            if not printer:
                print("TotemBridge: impressora não configurada")
                return False
            print_ticket(printer, data, get_app_dir())
            return True
        except Exception as exc:
            print(f"TotemBridge: erro ao imprimir senha: {exc}")
            return False

    @pyqtSlot(result=bool)
    def isAvailable(self) -> bool:
        return get_printer_name() is not None
