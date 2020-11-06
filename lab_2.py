from PyQt5 import QtCore, QtWidgets, QtGui
from ui.lab_2 import Ui_Form as ui_lab_2
from src.Core import v2
from numpy import linspace
from typing import Literal, Tuple, List


class DrawArea(QtWidgets.QWidget):
    current_index_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setGeometry(parent.geometry())
        self.mainPen = QtGui.QPen(QtGui.QColor(0x0d47a1), 2)
        self.highlightPen = QtGui.QPen(QtGui.QColor(0xFFA0A0), 3)
        self.points: List[v2] = [
            v2(( 10,  10)),
            v2(( 20, 200)),
            v2((500,  10))
        ]
        self.point = v2((0, 0))
        self.current_point = self.points[0]
        self.current_index = 0
        self.spline_points: List[v2] = []
        self.calculate_spline()
        self.mouse_grabbed = False

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # print(self.points)
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.setPen(self.mainPen)
        for i, point in enumerate(self.points):
            if i == self.current_index:
                self.painter.setPen(self.highlightPen)
                self.painter.drawEllipse(
                    point.to_QPoint(),
                    5, 5
                )
                self.painter.setPen(self.mainPen)
            else:
                self.painter.drawEllipse(
                    point.to_QPoint(),
                    5, 5
                )
        self.painter.drawPoint(self.point.to_QPoint())
        for point in self.spline_points:
            self.painter.drawPoint(point.to_QPoint())
        self.painter.end()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_grabbed:
            x, y = event.x(), event.y()
            self.move_point(x,y)
            self.current_index_changed.emit()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        for i, point in enumerate(self.points):
            if QtCore.QLineF(point.to_QPoint(), event.pos()).length() < 20:
                self.mouse_grabbed = True
                self.current_index = i
                self.current_index_changed.emit()
                return
        self.current_index = -1
        self.repaint()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.mouse_grabbed = False

    def set_point(self, x, y):
        self.point = v2((x, y))
        self.repaint()

    def calculate_spline(self):
        x = [point.x for point in self.points]
        y = [point.y for point in self.points]
        self.spline_points.clear()
        for t in linspace(0, 1, 100):
            tmp = (
                (1-t)**2*x[0] + 2*(1-t)*t*x[1] + t**2 * x[2],
                (1-t)**2*y[0] + 2*(1-t)*t*y[1] + t**2 * y[2]
            )
            self.spline_points.append(v2(tmp))

    def move_point(self, x, y):
        self.current_point = v2((x, y))
        ci = self.current_index
        self.points[ci] = v2((x,y))
        self.calculate_spline()
        self.repaint()

    def set_current_index(self, index):
        self.current_index = index


class Lab_2(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Lab_2, self).__init__(parent)
        self.ui: ui_lab_2 = ui_lab_2()
        self.ui.setupUi(self)
        self.drawArea = DrawArea(self.ui.drawArea)
        self.ui.drawArea = self.drawArea
        self.setup_connections()
        self.ui.comboBox.addItems(
            [str(x) for x in [1,2,3]]
        )

    def setup_connections(self):
        self.ui.comboBox.currentIndexChanged.connect(self.s_update_current_point)
        # self.ui.horizontalSlider.valueChanged.connect(self.s_update_point_position)
        # self.ui.verticalSlider.valueChanged.connect(self.s_update_point_position)
        self.drawArea.current_index_changed.connect(self.s_reveal_current_point)

    def s_update_sliders(self):
        self.drawArea.set_point(
            self.ui.horizontalSlider.value(),
            self.ui.verticalSlider.value()
        )

    def s_update_current_point(self):
        self.drawArea.set_current_index(self.ui.comboBox.currentIndex())
        ci = self.drawArea.current_index
        x, y = self.drawArea.points[ci].to_list()
        self.ui.horizontalSlider.setValue(x)
        self.ui.verticalSlider.setValue(y)
        self.drawArea.repaint()

    def s_update_point_position(self):
        x = self.ui.horizontalSlider.value()
        y = self.ui.verticalSlider.value()
        self.drawArea.move_point(x, y)
        # self.drawArea.points[i] = v2((x,y))
        # self.drawArea.current_point = v2((x,y))
        # self.drawArea.calculate_spline()
        # self.drawArea.repaint()

    def s_reveal_current_point(self):
        ci = self.drawArea.current_index
        x, y = self.drawArea.points[ci].to_list()
        if ci == -1:
            return
        else:
            self.ui.comboBox.setCurrentIndex(ci)
        self.ui.horizontalSlider.setValue(x)
        self.ui.verticalSlider.setValue(y)


