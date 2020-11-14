from PyQt5 import QtCore, QtWidgets, QtGui
from numpy.matrixlib.defmatrix import matrix
from ui.lab_3 import Ui_Form as ui_lab_3
from src.Core import v2, v3
from numpy import linspace
from typing import Literal, Tuple, List
from src.Surfaces import BilinearSurface


class DrawArea(QtWidgets.QWidget):
    current_index_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setGeometry(parent.geometry())
        self.mainPen = QtGui.QPen(QtGui.QColor(0x0d47a1), 2)
        self.highlightPen = QtGui.QPen(QtGui.QColor(0xFFA0A0), 3)
        self.surface_points = BilinearSurface.default_points
        self.current_rotation: Tuple[int] = (0,0,0)
        self.surface = BilinearSurface(self.surface_points)
        self.points: List[v3] = []
        self.m: matrix = matrix([])
        self.recalc()
        self.center = QtCore.QPoint(
            self.geometry().height() // 2,
            self.geometry().width() // 2
        )

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.setPen(self.mainPen)
        zip(self.points[1::2], self.points[0::2])
        for row in list(self.m):
            list_of_points: List[v3] = [x for x in row.flat]
            for a,b in zip(list_of_points[1::1], list_of_points[0::1]):
                self.painter.drawLine(
                    a.to_v2().to_QPoint() + self.center,
                    b.to_v2().to_QPoint() + self.center
                )
        for row in list(self.m.T):
            list_of_points: List[v3] = [x for x in row.flat]
            for a,b in zip(list_of_points[1::1], list_of_points[0::1]):
                self.painter.drawLine(
                    a.to_v2().to_QPoint() + self.center,
                    b.to_v2().to_QPoint() + self.center
                )

        self.painter.setPen(QtCore.Qt.red)
        a = self.surface.calculate(0,0)
        b = self.surface.calculate(0,1)
        c = self.surface.calculate(1,0)
        d = self.surface.calculate(1,1)
        for point, name in zip([a,b,c,d], ['A','B','C','D']):
            point.rotate(*self.current_rotation)
            tmp = point.to_v2().to_QPoint() + self.center
            self.painter.drawEllipse(tmp, 5.0, 5.0)
            self.painter.drawText(tmp, name)
        self.painter.end()

    def recalc(self):
        self.points.clear()
        for x in linspace(0, 1, 10):
            for y in linspace(0, 1, 10):
                self.points.append(
                    self.surface.calculate(x,y)
                )
        self.m = matrix(self.points)
        self.m.shape = (10,10)
    
    def rotate(self, x: int, y: int, z: int):
        self.surface = BilinearSurface(self.surface_points)
        self.current_rotation = (x,y,z)
        self.recalc()
        for point in self.points:
            point.rotate(x,y,z)

    def set_surface_points(self, points: List[list[int]]):
        a, b, c, d = points
        new_points = [
            [v3(a), v3(b)],
            [v3(c), v3(d)]
        ]
        self.surface_points = new_points
        # self.surface = BilinearSurface(new_points)
        # self.recalc()
        self.rotate(*self.current_rotation)
        self.repaint()


class Lab_3(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Lab_3, self).__init__(parent)
        self.ui: ui_lab_3 = ui_lab_3()
        self.ui.setupUi(self)
        self.drawArea = DrawArea(self.ui.drawArea)
        self.ui.drawArea = self.drawArea
        self.setup_connections()

    def setup_connections(self):
        self.ui.rotateAxisX.valueChanged.connect(self.s_rotate)
        self.ui.rotateAxisY.valueChanged.connect(self.s_rotate)
        self.ui.rotateAxisZ.valueChanged.connect(self.s_rotate)
        self.ui.spinA_x.valueChanged.connect(self.s_update_points)
        self.ui.spinA_y.valueChanged.connect(self.s_update_points)
        self.ui.spinA_z.valueChanged.connect(self.s_update_points)
        self.ui.spinB_x.valueChanged.connect(self.s_update_points)
        self.ui.spinB_y.valueChanged.connect(self.s_update_points)
        self.ui.spinB_z.valueChanged.connect(self.s_update_points)
        self.ui.spinC_x.valueChanged.connect(self.s_update_points)
        self.ui.spinC_y.valueChanged.connect(self.s_update_points)
        self.ui.spinC_z.valueChanged.connect(self.s_update_points)
        self.ui.spinD_x.valueChanged.connect(self.s_update_points)
        self.ui.spinD_y.valueChanged.connect(self.s_update_points)
        self.ui.spinD_z.valueChanged.connect(self.s_update_points)

    def s_rotate(self):
        self.ui.labelAxisX.setText(str(self.ui.rotateAxisX.value()))
        self.ui.labelAxisY.setText(str(self.ui.rotateAxisY.value()))
        self.ui.labelAxisZ.setText(str(self.ui.rotateAxisZ.value()))
        self.drawArea.rotate(
            self.ui.rotateAxisX.value(),
            self.ui.rotateAxisY.value(),
            self.ui.rotateAxisZ.value()
        )

    def s_update_points(self):
        a = [
            self.ui.spinA_x.value(),
            self.ui.spinA_y.value(),
            self.ui.spinA_z.value()
        ]
        b = [
            self.ui.spinB_x.value(),
            self.ui.spinB_y.value(),
            self.ui.spinB_z.value()
        ]
        c = [
            self.ui.spinC_x.value(),
            self.ui.spinC_y.value(),
            self.ui.spinC_z.value()
        ]
        d = [
            self.ui.spinD_x.value(),
            self.ui.spinD_y.value(),
            self.ui.spinD_z.value()
        ]
        self.drawArea.set_surface_points([a,b,c,d])
