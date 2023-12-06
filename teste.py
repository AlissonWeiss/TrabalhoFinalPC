from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QLabel, QSpinBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Criar a barra de ferramentas
        self.toolbar = QToolBar("Minha Toolbar")
        self.addToolBar(self.toolbar)

        # Adicionar um QLabel à barra de ferramentas
        self.label = QLabel("Distance between points: ")
        self.toolbar.addWidget(self.label)

        # Criar e configurar o QSpinBox
        self.spinBox = QSpinBox()
        self.spinBox.setMinimum(1)  # Valor mínimo
        self.spinBox.setMaximum(1000)  # Valor máximo
        self.spinBox.setValue(50)  # Valor padrão
        self.toolbar.addWidget(self.spinBox)

# Criando a aplicação
app = QApplication([])

# Criando a janela principal
main_window = MainWindow()
main_window.show()

# Executando a aplicação
app.exec_()
