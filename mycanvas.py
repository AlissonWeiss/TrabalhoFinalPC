from OpenGL.GL import *
from PyQt5 import QtOpenGL, QtCore
from PyQt5.QtGui import QMouseEvent
import numpy as np
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

        self.view_mode = "collector"
        self.distance_between_points = -1
        self.matrix_mesh_points = np.zeros((0, 0), dtype=Point)

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
        glClear(GL_COLOR_BUFFER_BIT)

        if self.view_mode == "collector":
            self.tessellate_beziers()
            self.draw_bezier_segments()
            self.draw_bezier_points()
            self.draw_bezier_temp_curve()
        if self.view_mode == "mesh_points":
            self.draw_mesh_points()
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

        if self.view_mode != "collector":
            return

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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        converted_point = self.convert_point_coordinates_to_universe(event.pos())
        self.predict_bezier(converted_point.x(), converted_point.y())
        self.update()

    # </editor-fold>

    # <editor-fold desc="Bezier functions">

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
        glColor3f(0.0, 0.9, 0.0)
        glPointSize(2.5)
        glBegin(GL_POINTS)

        for row in self.matrix_mesh_points:
            for item in row:
                if type(item) is not Point:
                    continue
                glVertex2f(item.getX(), item.getY())

        glEnd()

    def calculate_mesh_points(self, distance_between_points: int):
        self.distance_between_points = distance_between_points
        x_min, x_max, y_min, y_max = self.m_view.getBoundBox()

        x_qty = int((x_max - x_min) / self.distance_between_points)
        y_qty = int((y_max - y_min) / self.distance_between_points)

        self.matrix_mesh_points = np.zeros((x_qty, y_qty), dtype=Point)

        for i in range(x_qty):
            for j in range(y_qty):
                x_pos = x_min + self.distance_between_points * i
                y_pos = y_min + self.distance_between_points * j
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