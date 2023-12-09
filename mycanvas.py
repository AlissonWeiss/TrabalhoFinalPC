import json

import numpy as np
from OpenGL.GL import *
from PyQt5 import QtOpenGL, QtCore
from PyQt5.QtGui import QMouseEvent

from enums.view_mode_enum import ViewModeEnum
from hetool.compgeom.compgeom import CompGeom
from hetool.compgeom.tesselation import Tesselation
from hetool.geometry.point import Point
from hetool.he.hecontroller import HeController
from hetool.he.hemodel import HeModel
from hetool.he.heview import HeView


class MyCanvas(QtOpenGL.QGLWidget):
    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_w = 1
        self.m_h = 1
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0

        self.m_model = HeModel()
        self.m_controller = HeController(self.m_model)
        self.m_view = HeView(self.m_model)
        self.m_he_tolerance = 10.0

        self.m_control_points = []
        self.m_temp_curve = []

        self.view_mode = ViewModeEnum.COLLECTOR.value
        self.distance_between_points = -1
        self.matrix_mesh_points = np.zeros((0, 0), dtype=Point)
        self.matrix_connections_points = np.zeros((0, 0), dtype=list)

        self.select_start_point = Point(0, 0)
        self.select_end_point = Point(0, 0)
        self.is_selecting = False

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)

    def resizeGL(self, _w, _h):
        self.m_w = _w
        self.m_h = _h

        if self.m_model.isEmpty():
            self.scale_world_window(1.0)
        else:
            self.fit_world_to_viewport()

        glViewport(0, 0, _w, _h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def scale_world_window(self, _scale_factor):
        cx = 0.5 * (self.m_L + self.m_R)
        cy = 0.5 * (self.m_B + self.m_T)
        dx = (self.m_R - self.m_L) * _scale_factor
        dy = (self.m_T - self.m_B) * _scale_factor

        ratio_vp = self.m_h / self.m_w
        if dy > dx * ratio_vp:
            dx = dy / ratio_vp
        else:
            dy = dx * ratio_vp

        self.m_L = cx - 0.5 * dx
        self.m_R = cx + 0.5 * dx
        self.m_B = cy - 0.5 * dy
        self.m_T = cy + 0.5 * dy

        self.m_he_tolerance = 0.005 * (dx + dy)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def fit_world_to_viewport(self):
        if self.m_model.isEmpty():
            return

        self.m_L, self.m_R, self.m_B, self.m_T = self.m_view.getBoundBox()
        self.scale_world_window(1.1)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.view_mode == ViewModeEnum.COLLECTOR.value:
            self.tessellate_beziers()
            self.draw_bezier_segments()
            self.draw_bezier_points()
            self.draw_bezier_temp_curve()
        if self.view_mode in (ViewModeEnum.MESH_POINTS.value, ViewModeEnum.SELECT_POINTS.value, ViewModeEnum.DESELECT_POINTS.value):
            self.draw_mesh_points()
        if self.is_selecting and self.view_mode in (ViewModeEnum.SELECT_POINTS.value, ViewModeEnum.DESELECT_POINTS.value):
            self.draw_selecting_area()
        self.update()

    def clear_draws(self):
        print("Clear")
        self.m_model.clearAll()

        self.m_control_points = []
        self.m_temp_curve = []
        self.matrix_mesh_points = np.zeros((0, 0), dtype=Point)

        self.update()

    def convert_point_coordinates_to_universe(self, _pt: QMouseEvent.pos) -> QtCore.QPoint:
        d_x = self.m_R - self.m_L
        d_y = self.m_T - self.m_B

        m_x = _pt.x() * d_x / self.m_w
        m_y = (self.m_h - _pt.y()) * d_y / self.m_h

        recalculated_x = self.m_L + m_x
        recalculated_y = self.m_B + m_y

        return QtCore.QPointF(recalculated_x, recalculated_y)

    # <editor-fold desc="Mouse events">
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.view_mode == ViewModeEnum.COLLECTOR.value:
            self.collect_bezier(event)

        if self.view_mode in (ViewModeEnum.SELECT_POINTS.value, ViewModeEnum.DESELECT_POINTS.value) and self.is_selecting:
            self.select_points_inside_area(True if self.view_mode == ViewModeEnum.SELECT_POINTS.value else False)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        converted_point = self.convert_point_coordinates_to_universe(event.pos())
        self.predict_bezier(converted_point.x(), converted_point.y())
        self.select_end_point = self.convert_point_coordinates_to_universe(event.pos())
        self.update()

    def mousePressEvent(self, event):
        self.select_start_point = self.convert_point_coordinates_to_universe(event.pos())
        self.select_end_point = self.select_start_point
        self.is_selecting = True
        self.update()

    # </editor-fold>

    # <editor-fold desc="Bezier functions">

    def collect_bezier(self, event):
        pt = event.pos()
        converted_point = self.convert_point_coordinates_to_universe(pt)

        snap, xs, ys = self.m_view.snapToPoint(converted_point.x(), converted_point.y(), self.m_he_tolerance)
        if snap:
            is_complete = self.collect_point(xs, ys)
        else:
            snap, xs, ys = self.m_view.snapToSegment(converted_point.x(), converted_point.y(), self.m_he_tolerance)
            if snap:
                is_complete = self.collect_point(xs, ys)
            else:
                is_complete = self.collect_point(converted_point.x(), converted_point.y())

        if is_complete:
            self.setMouseTracking(False)
            curve = self.get_curve()
            he_segment = []
            for pt in curve:
                he_segment.append(pt[0])
                he_segment.append(pt[1])
            self.m_controller.insertSegment(he_segment, 0.01)
            self.update()
        else:
            self.setMouseTracking(True)

    def tessellate_beziers(self):
        patches = self.m_model.getPatches()
        for patch in patches:
            glColor3f(0.0, 0.9, 0.0)

            triangles = Tesselation.tessellate(patch.getPoints())
            for triangle in triangles:
                glBegin(GL_TRIANGLES)
                for pt in triangle:
                    glVertex2d(pt.getX(), pt.getY())
                glEnd()

    def draw_bezier_segments(self):
        segments = self.m_model.getSegments()
        for segment in segments:
            pts = segment.getPointsToDraw()
            glColor3f(0.0, 0.0, 0.7)
            glBegin(GL_LINE_STRIP)
            for pt in pts:
                glVertex2f(pt.getX(), pt.getY())
            glEnd()

    def draw_bezier_points(self):
        points = self.m_model.getPoints()
        glColor3f(1.0, 0.0, 0.0)
        glPointSize(7)
        glBegin(GL_POINTS)

        for point in points:
            glVertex2f(point.getX(), point.getY())
        glEnd()

    def draw_bezier_temp_curve(self):
        if len(self.m_temp_curve) > 0:
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            for pti in self.m_temp_curve:
                glVertex2f(pti[0], pti[1])
            glEnd()

    def predict_bezier(self, x, y):
        if len(self.m_control_points) == 0:
            pass
        elif len(self.m_control_points) == 1:
            self.m_temp_curve = [self.m_control_points[0], [x, y]]
        elif len(self.m_control_points) == 2:
            n_sampling = 10
            self.m_temp_curve = []
            for ii in range(n_sampling+1):
                t = ii/n_sampling
                ptx, pty = self.calculate_bezier_x_and_y(t, x, y)
                self.m_temp_curve.append([ptx, pty])

    def get_curve(self):
        curve = self.m_temp_curve
        self.m_control_points = []
        self.m_temp_curve = []
        return curve

    def collect_point(self, x, y):
        is_complete = False

        if len(self.m_control_points) == 0:
            self.m_control_points.append([x, y])
        elif len(self.m_control_points) == 1:
            self.m_control_points.append([x, y])
        elif len(self.m_control_points) == 2:
            self.m_control_points.append([x, y])
            is_complete = True
        return is_complete

    def calculate_bezier_x_and_y(self, t: float, x, y):
        bezier_x = (1 - t) ** 2 * self.m_control_points[0][0] + 2 * (1 - t) * t * x + t ** 2 * self.m_control_points[1][0]
        bezier_y = (1 - t) ** 2 * self.m_control_points[0][1] + 2 * (1 - t) * t * y + t ** 2 * self.m_control_points[1][1]

        return bezier_x, bezier_y

    # </editor-fold>

    # <editor-fold desc="Mesh points">

    def draw_mesh_points(self):
        glPointSize(3)
        glBegin(GL_POINTS)

        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue
                if item.isSelected():
                    glColor3f(0.9, 0.0, 0.0)
                else:
                    if item.isFixedX() or item.isFixedY():
                        glColor3f(0.9, 0.9, 0.05)
                    elif item.getXForce() != 0 or item.getYForce() != 0:
                        glColor3f(0.0, 0.0, 1.0)
                    else:
                        glColor3f(0.0, 0.9, 0.0)
                glVertex2f(item.getX(), item.getY())

        glEnd()

    def draw_selecting_area(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBegin(GL_QUADS)
        glColor4f(0.0, 0.0, 1, 0.3)  # Cor azul
        glVertex2f(self.select_start_point.x(), self.select_start_point.y())
        glVertex2f(self.select_end_point.x(), self.select_start_point.y())
        glVertex2f(self.select_end_point.x(), self.select_end_point.y())
        glVertex2f(self.select_start_point.x(), self.select_end_point.y())
        glEnd()

        glDisable(GL_BLEND)

    def calculate_mesh_points(self, distance_between_points: int):
        self.distance_between_points = distance_between_points
        x_min, x_max, y_min, y_max = self.m_view.getBoundBox()

        x_qty = int((x_max - x_min) / self.distance_between_points)
        y_qty = int((y_max - y_min) / self.distance_between_points)

        self.matrix_mesh_points = np.zeros((y_qty, x_qty), dtype=Point)

        for i in range(y_qty):
            for j in range(x_qty):
                x_pos = x_min + self.distance_between_points * j
                y_pos = y_min + self.distance_between_points * i
                point = Point(x_pos, y_pos)
                patches = self.m_view.getPatches()
                for patch in patches:
                    if CompGeom.isPointInPolygon(patch.getPoints(), point):
                        self.matrix_mesh_points[i][j] = point
                        break

    def alternate_view(self, view_mode):
        self.view_mode = view_mode
        self.on_view_mode_updated()

    def on_view_mode_updated(self):
        self.update()

    # </editor-fold>

    def select_points_inside_area(self, select: bool):
        x1 = min(self.select_start_point.x(), self.select_end_point.x())
        x2 = max(self.select_start_point.x(), self.select_end_point.x())
        y1 = min(self.select_start_point.y(), self.select_end_point.y())
        y2 = max(self.select_start_point.y(), self.select_end_point.y())

        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue

                px, py = item.getX(), item.getY()

                if x1 <= px <= x2 and y1 <= py <= y2:
                    item.setSelected(select)

    def reset_selected_points(self):
        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue
                item.setSelected(False)
                item.setFixedX(False)
                item.setFixedY(False)
                item.setXForce(0.0)
                item.setYForce(0.0)

    def export_pvc_data(self, file_name: str):
        num_rows, num_columns = self.get_number_of_rows_and_columns(self.matrix_mesh_points)

        self.build_connect_through_matrix(num_rows, num_columns)

        # self.matrix_connections_points = np.zeros((num_rows, num_columns), dtype=list)
        #
        # np_data = {"ref": self.matrix_mesh_points}
        # json_data = json.dumps(np_data, cls=NumpyArrayEncoder)
        #
        # with open(f"{file_name}.json", "w") as file:
        #     file.write(json_data)

    def export_pvi_data(self, file_name: str):
        num_rows, num_columns = self.get_number_of_rows_and_columns(self.matrix_mesh_points)

        file_data = {
            "coordinates": self.build_list_coordinate_through_matrix(),
            "connect": self.build_connect_through_matrix(num_rows, num_columns),
            "restrictions": self.build_list_restrictions_through_matrix(),
            "forces": self.build_list_forces_through_matrix()
        }

        with open(f"{file_name}.json", "w") as file:
            file.write(json.dumps(file_data, default=json_serial, indent=4))

    def build_list_coordinate_through_matrix(self):
        coordinates = []
        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue
                coordinates.append([item.getX(), item.getY()])

        return coordinates

    def build_list_restrictions_through_matrix(self):
        restrictions = []
        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue
                restrictions.append([item.isFixedX(), item.isFixedY()])

        return restrictions

    def build_list_forces_through_matrix(self):
        forces = []
        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue
                forces.append([item.getXForce(), item.getYForce()])

        return forces

    def build_connect_through_matrix(self, num_rows: int, num_columns: int):
        matrix = self.matrix_mesh_points
        aux_matrix = self.build_temp_matrix_for_connections(num_rows, num_columns)
        connections = []
        for row in range(num_rows):
            for column in range(num_columns):
                item = matrix[row][column]
                if type(item) is not Point:
                    continue

                items_list = []
                for direction in ["left", "right", "top", "down"]:
                    items_list.append(self.get_connect_by_direction(direction, aux_matrix, row, column, num_rows, num_columns))

                lista = [len([i for i in items_list if i != 0])]
                lista.extend(items_list)
                connections.append(lista)

        return connections

    def build_temp_matrix_for_connections(self, num_rows: int, num_columns: int):
        index = 1

        matrix = np.zeros((num_rows, num_columns), dtype=np.int32)

        for i in range(num_rows):
            for j in range(num_columns):
                item = self.matrix_mesh_points[i][j]
                if type(item) is not Point:
                    continue
                matrix[i][j] = index
                index += 1

        return matrix

    def get_connect_by_direction(self, direction: str, indexed_items_matrix, row: int, column: int, num_rows: int, num_columns: int):
        if direction == "left":
            column -= 1
            if column < 0:
                return 0
        elif direction == "right":
            column += 1
            if column > num_columns:
                return 0
        elif direction == "top":
            row -= 1
            if row < 0:
                return 0
        elif direction == "down":
            row += 1
            if row > num_rows:
                return 0

        try:
            item = self.matrix_mesh_points[row][column]
            if type(item) is Point:
                return self.get_index_of_item(indexed_items_matrix, item)
            else:
                return 0
        except:
            return 0

    def get_index_of_item(self, indexed_items_matrix: np.matrix, point: Point):
        for idx, val in np.ndenumerate(self.matrix_mesh_points):
            if type(val) is not Point:
                continue
            if val == point:
                row, column = idx
                return indexed_items_matrix[row][column]
        return 0

    @staticmethod
    def get_number_of_rows_and_columns(matrix):
        return np.shape(matrix)

    def pvi_define_selected_points_as_fixed(self, fixed_x, fixed_y):
        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue

                if item.isSelected():
                    item.setFixedX(fixed_x)
                    item.setFixedY(fixed_y)
                    # print(f"Item: {item.getX()}, {item.getY()}, {item.isFixedX()}, {item.isFixedY()}")

    def pvi_define_force_selected_points_event(self, _force_x: float, _force_y: float):
        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue

                if item.isSelected():
                    item.setXForce(_force_x)
                    item.setYForce(_force_y)
                    print(f"Item: {item.getX()}, {item.getY()}, {item.getXForce()}, {item.getYForce()}")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, np.int32):
        return int(obj)
    raise TypeError("Type %s not serializable" % type(obj))
