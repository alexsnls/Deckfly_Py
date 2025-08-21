import sys
import subprocess
import json
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QDialog, QListWidget, QInputDialog, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

ARQUIVO_PERFIS = "perfis.json"

# ---------------- Funções para persistência ----------------
def carregar_perfis():
    if os.path.exists(ARQUIVO_PERFIS):
        with open(ARQUIVO_PERFIS, "r") as f:
            return json.load(f)
    else:
        return {"Estudo": [], "Jogos": [], "Trabalho": []}

def salvar_perfis(perfis):
    with open(ARQUIVO_PERFIS, "w") as f:
        json.dump(perfis, f, indent=4)

# ---------------- Widget de perfil ----------------
class PerfilWidget(QWidget):
    def __init__(self, nome, icone, programas, perfis_dict):
        super().__init__()
        self.nome = nome
        self.programas = programas
        self.perfis_dict = perfis_dict
        self.setFixedSize(150, 150)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.btn_perfil = QPushButton()
        self.btn_perfil.setIcon(icone)
        self.btn_perfil.setIconSize(QSize(64, 64))
        self.btn_perfil.setFixedSize(100, 100)
        self.btn_perfil.setStyleSheet("""
            QPushButton {
                border-radius: 50px;
                background-color: #555555;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        self.btn_perfil.clicked.connect(self.abrir_programas)

        self.label = QLabel(nome)
        self.label.setAlignment(Qt.AlignCenter)

        self.btn_editar = QPushButton("Editar")
        self.btn_editar.setVisible(False)
        self.btn_editar.setStyleSheet("background-color: #222222; color: white; border-radius: 5px;")
        self.btn_editar.clicked.connect(self.editar_programas)

        self.layout.addWidget(self.btn_perfil)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btn_editar)
        self.setLayout(self.layout)

    def enterEvent(self, event):
        self.btn_editar.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_editar.setVisible(False)
        super().leaveEvent(event)

    def abrir_programas(self):
        for caminho in self.programas:
            try:
                subprocess.Popen(caminho)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível abrir {caminho}\n{e}")

    def editar_programas(self):
        dialog = EditarDialog(self.nome, self.programas, self.perfis_dict)
        dialog.exec()
        # Atualiza lista de programas depois de editar
        self.programas = self.perfis_dict[self.nome]

# ---------------- Dialog de edição ----------------
class EditarDialog(QDialog):
    def __init__(self, nome, programas, perfis_dict):
        super().__init__()
        self.setWindowTitle(f"Editar programas - {nome}")
        self.setFixedSize(400, 300)
        self.nome = nome
        self.perfis_dict = perfis_dict
        self.programas = programas.copy()

        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.programas)

        btn_add = QPushButton("Adicionar programa")
        btn_remove = QPushButton("Remover selecionado")
        btn_add.clicked.connect(self.adicionar_programa)
        btn_remove.clicked.connect(self.remover_programa)

        layout.addWidget(self.list_widget)
        layout.addWidget(btn_add)
        layout.addWidget(btn_remove)
        self.setLayout(layout)

    def adicionar_programa(self):
        caminho, ok = QInputDialog.getText(self, "Adicionar programa", "Digite o caminho completo do programa:")
        if ok and caminho:
            self.programas.append(caminho)
            self.list_widget.addItem(caminho)
            self.perfis_dict[self.nome] = self.programas
            salvar_perfis(self.perfis_dict)  # salva no JSON

    def remover_programa(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.programas.remove(item.text())
            self.list_widget.takeItem(self.list_widget.row(item))
            self.perfis_dict[self.nome] = self.programas
            salvar_perfis(self.perfis_dict)  # salva no JSON

# ---------------- Janela principal ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeckFly - Perfis")
        self.setGeometry(200, 200, 600, 400)
        self.setFixedSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        layout.setSpacing(40)
        layout.setAlignment(Qt.AlignCenter)

        self.perfis_dict = carregar_perfis()

        self.perfis = [
            PerfilWidget("Estudo", qta.icon("fa5s.brain", color="white"), self.perfis_dict["Estudo"], self.perfis_dict),
            PerfilWidget("Jogos", qta.icon("fa5s.gamepad", color="white"), self.perfis_dict["Jogos"], self.perfis_dict),
            PerfilWidget("Trabalho", qta.icon("fa5s.briefcase", color="white"), self.perfis_dict["Trabalho"], self.perfis_dict)
        ]

        for perfil in self.perfis:
            layout.addWidget(perfil)

        central_widget.setLayout(layout)

# ---------------- Execução ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
