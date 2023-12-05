from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QDesktopWidget, QMenuBar, QMenu

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
        # # create a model object and pass to canvas
        # self.model = MyModel()
        # self.canvas.set_model(self.model)
        # create a Toolbar

        menu_bar = QMenuBar(self)
        # Creating menus using a QMenu object
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        # Creating menus using a title
        edit_menu = menu_bar.addMenu("&Edit")
        help_menu = menu_bar.addMenu("&Help")

        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(help_menu)

        self.setMenuBar(menu_bar)

        tb = self.addToolBar("File")
        fit = QAction(QIcon("icons/reset_icon.png"), "reset", self)
        tb.addAction(fit)
        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self, a):
        if a.text() == "reset":
            #self.canvas.fit_world_to_viewport()
            self.canvas.clear_draws()
