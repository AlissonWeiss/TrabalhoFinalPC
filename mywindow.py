from PyQt5.QtWidgets import QMainWindow, QAction, QDesktopWidget, QMenuBar, QMenu, QInputDialog, QMessageBox

from mycanvas import *


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        geometry = QDesktopWidget().availableGeometry()
        width = int(geometry.width() * 0.8)
        height = int(geometry.height() * 0.8)

        self.setFixedSize(width, height)
        self.setWindowTitle("Modelador - Alisson Weiss - 216.031.083")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)

        self.__create_menus()

    def __create_menus(self):
        menu_bar = QMenuBar(self)

        tools_menu = QMenu("&Tools", self)

        # Cria os itens dentro dos menus
        self.reset_action = QAction("&Reset all drawings ", self)
        self.reset_action.triggered.connect(self.clear_all_drawings_event)

        self.tesselation_mesh = QAction("&View tessellation mesh", self)
        self.tesselation_mesh.triggered.connect(self.view_tesselation_mesh_event)

        self.export_json_data = QAction("&Export JSON data", self)
        self.export_json_data.triggered.connect(self.export_json_data_event)

        tools_menu.addAction(self.reset_action)
        tools_menu.addAction(self.tesselation_mesh)
        tools_menu.addSeparator()
        tools_menu.addAction(self.export_json_data)

        menu_bar.addMenu(tools_menu)
        self.setMenuBar(menu_bar)

    def clear_all_drawings_event(self):
        self.canvas.clear_draws()

    def view_tesselation_mesh_event(self):
        value, ok = QInputDialog.getInt(self, 'Espaçamento entre pontos',
                                        'Informe o espaçamento entre os pontos da malha: ')
        if ok:
            print(value)

    def export_json_data_event(self):
        mesh_points_distance, ok = QInputDialog.getInt(self, 'Espaçamento entre pontos',
                                                       'Informe o espaçamento entre os pontos da malha: ')
        if ok:
            if mesh_points_distance <= 0:
                QMessageBox.about(self, "Valor inválido", "O valor do espaçamento deve ser maior que zero.")
                return
        else:
            return

        file_name, ok = QInputDialog.getText(self, 'Nome do arquivo',
                                                   'Informe o nome do arquivo a ser salvo: ')
        if ok:
            if file_name == "" or file_name is None:
                QMessageBox.about(self, "Valor inválido", "O nome do arquivo deve possuir pelo menos um caractere.")
                return
        else:
            return
