from PyQt6.QtCore import QUrl
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEngineScript
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from totem.bridge import TotemBridge


class KioskScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        self._setup_web_channel()
        layout.addWidget(self.browser)
        self.setLayout(layout)

    def _setup_web_channel(self):
        self.bridge = TotemBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("totemBridge", self.bridge)

        page = self.browser.page()
        page.setWebChannel(self.channel)

        script = QWebEngineScript()
        script.setSourceUrl(QUrl("qrc:///qtwebchannel/qwebchannel.js"))
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(False)
        page.scripts().insert(script)

    def load_url(self, url: str):
        self.browser.setUrl(QUrl(url))
