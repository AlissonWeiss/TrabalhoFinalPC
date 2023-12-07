from PyQt5.QtWidgets import QMainWindow, QAction, QDesktopWidget, QMenuBar, QMenu, QInputDialog, QMessageBox, QLabel, \
    QSpinBox, QDialog, QVBoxLayout, QPushButton

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
        menu_bar.addMenu(self.__create_pvc_menu())
        menu_bar.addMenu(self.__create_pvi_menu())

        self.setMenuBar(menu_bar)

        toolbar = self.addToolBar("Toolbar")

        action_reset_drawings = QAction("&Reset all drawings [F1]", self)
        action_reset_drawings.setShortcut("F1")
        action_reset_drawings.action_id = 1
        toolbar.addAction(action_reset_drawings)

        toolbar.addSeparator()

        calculate_grid_points = QAction("&Calculate grid of points [F2]", self)
        calculate_grid_points.setShortcut("F2")
        calculate_grid_points.action_id = 2
        toolbar.addAction(calculate_grid_points)

        toolbar.addSeparator()

        self.action_view_points = QAction("&View points [F3]", self)
        self.action_view_points.setShortcut("F3")
        self.action_view_points.setCheckable(True)
        self.action_view_points.action_id = 3
        toolbar.addAction(self.action_view_points)

        toolbar.addSeparator()

        self.select_points = QAction("&Select points [F4]", self)
        self.select_points.setShortcut("F4")
        self.select_points.setCheckable(True)
        self.select_points.action_id = 4
        toolbar.addAction(self.select_points)

        toolbar.addSeparator()

        self.deselect_points = QAction("&Deselect points [F5]", self)
        self.deselect_points.setShortcut("F5")
        self.deselect_points.setCheckable(True)
        self.deselect_points.action_id = 5
        toolbar.addAction(self.deselect_points)

        toolbar.addSeparator()

        self.label = QLabel("Distance between points: ")
        toolbar.addWidget(self.label)

        # Criar e configurar o QSpinBox
        self.distance_between_points = QSpinBox()
        self.distance_between_points.setMinimum(1)
        self.distance_between_points.setMaximum(1000)
        self.distance_between_points.setValue(20)
        toolbar.addWidget(self.distance_between_points)

        toolbar.actionTriggered[QAction].connect(self.on_toolbar_click)

    def __create_pvc_menu(self):
        menu = QMenu("&PVC", self)

        self.select_side_input_temp = QAction("&1. Select side to input temperature", self)
        self.select_side_input_temp.triggered.connect(self.calculate_mesh_points_event)

        self.export_json_data_pvc = QAction("&2. Export JSON data", self)
        self.export_json_data_pvc.triggered.connect(self.export_json_data_pcv_event)

        menu.addAction(self.select_side_input_temp)
        menu.addAction(self.export_json_data_pvc)

        return menu

    def __create_pvi_menu(self):
        menu = QMenu("&PVI", self)

        self.pvi_input_force = QAction("&1. Input force on selected points", self)
        self.pvi_input_force.triggered.connect(self.pvi_define_force_selected_points_event)

        self.pvi_define_fixed_points = QAction("&2. Define selected points as as fixed", self)
        self.pvi_define_fixed_points.triggered.connect(self.pvi_define_fixed_points_event)

        self.export_json_data_pvi = QAction("&3. Export JSON data", self)
        self.export_json_data_pvi.triggered.connect(self.export_json_data_pvi_event)

        self.reset_selected_points_pvi = QAction("&4. Reset selected points", self)
        self.reset_selected_points_pvi.triggered.connect(self.reset_selected_points)

        menu.addAction(self.pvi_input_force)
        menu.addAction(self.pvi_define_fixed_points)
        menu.addAction(self.export_json_data_pvi)
        menu.addSeparator()
        menu.addAction(self.reset_selected_points_pvi)

        return menu

    def on_toolbar_click(self, action):
        if action.action_id == 1:
            self.canvas.clear_draws()
        elif action.action_id == 2:
            self.calculate_mesh_points_event()
        elif action.action_id == 3:
            self.select_points.setChecked(False)
            self.deselect_points.setChecked(False)
            if action.isChecked():
                self.canvas.alternate_view(ViewModeEnum.MESH_POINTS.value)
            else:
                self.canvas.alternate_view(ViewModeEnum.COLLECTOR.value)
        elif action.action_id == 4:
            self.action_view_points.setChecked(False)
            self.deselect_points.setChecked(False)

            if action.isChecked():
                self.canvas.alternate_view(ViewModeEnum.SELECT_POINTS.value)
            else:
                self.canvas.alternate_view(ViewModeEnum.MESH_POINTS.value)
                self.action_view_points.setChecked(True)
        elif action.action_id == 5:
            self.action_view_points.setChecked(False)
            self.select_points.setChecked(False)
            if action.isChecked():
                self.canvas.alternate_view(ViewModeEnum.DESELECT_POINTS.value)
            else:
                self.canvas.alternate_view(ViewModeEnum.MESH_POINTS.value)
                self.action_view_points.setChecked(True)

    def clear_all_drawings_event(self):
        self.canvas.clear_draws()

    def calculate_mesh_points_event(self):
        self.canvas.calculate_mesh_points(self.distance_between_points.value())

    def export_json_data_pcv_event(self):

        file_name, ok = QInputDialog.getText(self, 'Nome do arquivo',
                                                   'Informe o nome do arquivo a ser salvo: ')
        if ok:
            if file_name == "" or file_name is None:
                QMessageBox.about(self, "Valor inválido", "O nome do arquivo deve possuir pelo menos um caractere.")
                return
            self.canvas.export_pvc_data(file_name)
        else:
            return

    def export_json_data_pvi_event(self):

        file_name, ok = QInputDialog.getText(self, 'Nome do arquivo',
                                                   'Informe o nome do arquivo a ser salvo: ')
        if ok:
            if file_name == "" or file_name is None:
                QMessageBox.about(self, "Valor inválido", "O nome do arquivo deve possuir pelo menos um caractere.")
                return
            self.canvas.export_pvi_data(file_name)
        else:
            return

    def reset_selected_points(self):
        self.canvas.reset_selected_points()

    def pvi_define_fixed_points_event(self):
        self.canvas.pvi_define_selected_points_as_fixed()

    def pvi_define_force_selected_points_event(self):
        self.show_dialog("input_pvi_force")

        #self.canvas.pvi_define_force_selected_points_event(1, 2)

    def show_dialog(self, which_layout):
        self.dialog = QDialog()
        self.dialog.setFixedWidth(350)
        self.dialog.setFixedHeight(150)

        self.dialog_layout = QVBoxLayout(self)
        self.dialog_layout.layout_name = which_layout

        if which_layout == "input_pvi_force":
            self.dialog.setWindowTitle("Define applied force on selected points")

            self.dialog_layout.addWidget(QLabel("Applied force on X: "))
            self.x_applied_force = QSpinBox(self)
            self.x_applied_force.setMinimum(-999999)
            self.x_applied_force.setMaximum(999999)
            self.dialog_layout.addWidget(self.x_applied_force)

            self.dialog_layout.addWidget(QLabel("Applied force on Y: "))
            self.y_applied_force = QSpinBox(self)
            self.y_applied_force.setMinimum(-999999)
            self.y_applied_force.setMaximum(999999)
            self.dialog_layout.addWidget(self.y_applied_force)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.dialog_ok_clicked)

        self.dialog_layout.addWidget(ok_button)
        self.dialog.setLayout(self.dialog_layout)

        self.dialog.exec_()

    def dialog_ok_clicked(self):
        if self.dialog_layout.layout_name == "input_pvi_force":
        #if e == "input_pvi_force":
            x_force = self.x_applied_force.value()
            y_force = self.y_applied_force.value()
            self.canvas.pvi_define_force_selected_points_event(x_force, y_force)
        self.dialog.close()
