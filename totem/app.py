from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from totem.config_screen import ConfigScreen
from totem.kiosk_screen import KioskScreen


class TotemApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Totem")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.config_screen = ConfigScreen(self)
        self.kiosk_screen = KioskScreen(self)

        self.stack.addWidget(self.config_screen)
        self.stack.addWidget(self.kiosk_screen)

        self.show_config()

    def show_config(self):
        self.showNormal()
        self.stack.setCurrentWidget(self.config_screen)

    def start_kiosk(self, url: str):
        self.kiosk_screen.load_url(url)
        self.stack.setCurrentWidget(self.kiosk_screen)
        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.show_config()
        super().keyPressEvent(event)


def run():
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TotemApp()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())
