import json
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


def read_json_file(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data['temperatures'], int(data['rows']), int(data['columns'])


def color_by_temperature(temperature, max_temperature):
    intensity = int(255 * (temperature / max_temperature))
    return QColor(255, 255 - intensity, 255 - intensity)


class TemperatureVisualizer(QMainWindow):
    def __init__(self, data, rows, columns):
        super().__init__()

        self.data = data
        self.rows = rows
        self.columns = columns
        self.max_temperature = max(max(row) for row in data)

        self.ui()

    def ui(self):
        self.setWindowTitle("Distribuição de Temperatura - PVC")

        self.table = QTableWidget(self)
        self.table.setRowCount(self.rows)
        self.table.setColumnCount(self.columns)

        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                item = QTableWidgetItem(f"{self.data[i][j]:.2f}")
                item.setTextAlignment(Qt.AlignCenter)
                cor = color_by_temperature(self.data[i][j], self.max_temperature)
                item.setBackground(cor)

                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == '__main__':
    temperatures, rows, columns = read_json_file('output_pvc.json')

    app = QApplication(sys.argv)
    ex = TemperatureVisualizer(temperatures, rows, columns)
    ex.show()
    sys.exit(app.exec_())
