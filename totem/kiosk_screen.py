from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class KioskScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        self.setLayout(layout)

    def load_url(self, url: str):
        self.browser.setUrl(QUrl(url))
