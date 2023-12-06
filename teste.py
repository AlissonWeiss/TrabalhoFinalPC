from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt


class MyCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.startPoint = QPoint()
        self.endPoint = QPoint()
        self.isSelecting = False
        self.points = [(50, 50), (100, 100), (150, 150)]  # Exemplo de pontos
        self.selectedPoints = []

    def mousePressEvent(self, event):
        self.startPoint = event.pos()
        self.endPoint = self.startPoint
        self.isSelecting = True
        self.update()

    def mouseMoveEvent(self, event):
        self.endPoint = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.isSelecting = False
        self.selectPoints()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        painter.setPen(pen)

        # Desenhar pontos
        for point in self.points:
            painter.drawPoint(point[0], point[1])

        # Desenhar área de seleção
        if self.isSelecting:
            brush = QBrush(Qt.blue, Qt.DiagCrossPattern)
            painter.setBrush(brush)
            rect = QRect(self.startPoint, self.endPoint)
            painter.drawRect(rect)

    def selectPoints(self):
        rect = QRect(self.startPoint, self.endPoint)
        self.selectedPoints = [p for p in self.points if rect.contains(QPoint(p[0], p[1]))]
        print("Pontos selecionados:", self.selectedPoints)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvas = MyCanvas(self)
        self.setCentralWidget(self.canvas)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
