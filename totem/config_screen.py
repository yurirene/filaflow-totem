import json
import os

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from totem.config_store import get_paper_width_mm
from totem.paths import get_config_path
from totem.printing import list_printers, print_ticket, sample_ticket_data


class ConfigScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        layout = QVBoxLayout()

        title = QLabel("Configuração do Totem")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        layout.addWidget(QLabel("URL do Sistema:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://seu-sistema.com/totem")
        self.url_input.setMinimumHeight(40)
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("Selecionar Impressora:"))
        self.printer_combo = QComboBox()
        self.printer_combo.setMinimumHeight(40)
        self.load_printers()
        layout.addWidget(self.printer_combo)

        layout.addWidget(QLabel("Largura da Bobina:"))
        self.paper_combo = QComboBox()
        self.paper_combo.setMinimumHeight(40)
        self.paper_combo.addItem("58 mm (bobina estreita)", 58)
        self.paper_combo.addItem("80 mm (bobina larga)", 80)
        layout.addWidget(self.paper_combo)

        btn_layout = QHBoxLayout()

        self.test_print_btn = QPushButton("Emitir Impressão de Teste")
        self.test_print_btn.setMinimumHeight(50)
        self.test_print_btn.clicked.connect(self.test_print)
        btn_layout.addWidget(self.test_print_btn)

        self.save_btn = QPushButton("Salvar e Iniciar Kiosk")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.save_btn.clicked.connect(self.save_and_start)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        self.setLayout(layout)
        self.load_config()

    def selected_paper_width(self) -> int:
        return self.paper_combo.currentData()

    def load_printers(self):
        try:
            for printer in list_printers():
                self.printer_combo.addItem(printer)
            if self.printer_combo.count() == 0:
                self.printer_combo.addItem("Nenhuma impressora encontrada")
        except Exception as e:
            self.printer_combo.addItem("Erro ao carregar impressoras")
            print(f"Erro: {e}")

    def test_print(self):
        printer_name = self.printer_combo.currentText()
        if not printer_name or "Erro" in printer_name or "Nenhuma" in printer_name:
            QMessageBox.warning(self, "Erro", "Selecione uma impressora válida.")
            return

        try:
            paper_mm = self.selected_paper_width()
            print_ticket(
                printer_name,
                sample_ticket_data(),
                os.path.dirname(get_config_path()),
                paper_mm,
            )
            QMessageBox.information(
                self,
                "Sucesso",
                f"Teste enviado para {printer_name} ({paper_mm} mm).",
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao imprimir: {e}")

    def load_config(self):
        config_path = get_config_path()
        if not os.path.exists(config_path):
            return
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
            self.url_input.setText(config.get("url", ""))
            index = self.printer_combo.findText(config.get("printer", ""))
            if index >= 0:
                self.printer_combo.setCurrentIndex(index)

            paper_mm = get_paper_width_mm()
            paper_index = self.paper_combo.findData(paper_mm)
            if paper_index >= 0:
                self.paper_combo.setCurrentIndex(paper_index)
        except OSError:
            pass

    def save_and_start(self):
        url = self.url_input.text()
        printer = self.printer_combo.currentText()
        paper_mm = self.selected_paper_width()

        if not url.startswith("http"):
            QMessageBox.warning(self, "Erro", "A URL deve ser válida (começar com http).")
            return

        config = {
            "url": url,
            "printer": printer,
            "paper_width_mm": paper_mm,
        }
        with open(get_config_path(), "w", encoding="utf-8") as f:
            json.dump(config, f)

        self.parent_window.start_kiosk(url)
