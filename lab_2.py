from PyQt5 import QtCore, QtWidgets, QtGui
from src.Curves import Bezier
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
        self.minorPen = QtGui.QPen(QtGui.QColor(0xAFAFAF), 1)
        self.mouse_grabbed = False
        self.curve = Bezier()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.setPen(self.mainPen)
        for i, point in enumerate(self.curve.points):
            if i == self.curve.current_index:
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
        for point in self.curve.spline_points:
            self.painter.drawPoint(point.to_QPoint())
        self.painter.setPen(self.minorPen)
        for i, point in enumerate(self.curve.points):
            if i != 0:
                self.painter.drawLine(
                    self.curve.points[i-1].to_QPoint(),
                    self.curve.points[i].to_QPoint()
                )
        self.painter.end()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_grabbed:
            x, y = event.x(), event.y()
            self.move_point(x,y)
            self.current_index_changed.emit()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        print('mouse grab:', self.curve.points, '<-', (event.pos().x(), event.pos().y()))
        for i, point in enumerate(self.curve.points):
            if QtCore.QLineF(point.to_QPoint(), event.pos()).length() < 20:
                self.mouse_grabbed = True
                self.curve.current_index = i
                self.current_index_changed.emit()
                return
        # self.curve.current_index = -1
        self.mouse_grabbed = False
        self.repaint()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.mouse_grabbed = False

    def set_point(self, x, y):
        self.point = v2((x, y))
        self.repaint()

    def move_point(self, x, y):
        self.curve.current_point = v2((x, y))
        ci = self.curve.current_index
        if ci == -1:
            return
        self.curve.points[ci] = v2((x,y))
        self.curve.calculate()
        self.repaint()

    def add_point(self):
        # print(self.curve.points)
        last = self.curve.points[-1]
        points = self.curve.points[:-1]
        points.extend(
            [
                v2((500, 500)),
                last
            ]
        )
        self.curve = Bezier(points)
        self.curve.calculate()
        self.repaint()

    def remove_point(self):
        points = self.curve.points[:-2] + [self.curve.points[-1],]
        self.curve = Bezier(points)
        self.curve.calculate()
        self.repaint()


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
        self.ui.addPointButton.clicked.connect(self.s_add_point)
        self.ui.removePointButton.clicked.connect(self.s_remove_point)

    def s_update_sliders(self):
        self.drawArea.set_point(
            self.ui.horizontalSlider.value(),
            self.ui.verticalSlider.value()
        )

    def s_update_current_point(self):
        self.drawArea.curve.set_current_index(self.ui.comboBox.currentIndex())
        ci = self.drawArea.curve.current_index
        x, y = self.drawArea.curve.points[ci].to_list()
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
        ci = self.drawArea.curve.current_index
        x, y = self.drawArea.curve.points[ci].to_list()
        if ci == -1:
            return
        else:
            self.ui.comboBox.setCurrentIndex(ci)
        self.ui.horizontalSlider.setValue(x)
        self.ui.verticalSlider.setValue(y)

    def s_add_point(self):
        self.drawArea.add_point()

    def s_remove_point(self):
        self.drawArea.remove_point()
