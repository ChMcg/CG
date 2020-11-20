from PyQt5 import QtCore, QtWidgets, QtGui
from sip import delete
from ui.lab_4 import Ui_Form as ui_lab_4
from src.Core import Point, v2, v3
from src.Figures import Line, Polygon
from typing import Literal, Tuple, List
from src.Surfaces import BilinearSurface
from random import randint


class DrawArea(QtWidgets.QWidget):
    mainPen         = QtGui.QPen(QtGui.QColor(0x0d47a1), 1)
    highlightPen    = QtGui.QPen(QtGui.QColor(0xFFA0A0), 3)
    borderPen       = QtGui.QPen(QtGui.QColor(0xA0A0A0), 4)

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.mouse_grabbed = False
        self.setGeometry(parent.geometry())
        self.setMinimumSize(550, 550)
        # self.setSizePolicy(parent.sizePolicy())
        parent.resize(parent.minimumSize())
        self.handle_resize()
        self.line = Line(v2([20, 20]), v2([50, 60]))
        self.lines: List[Line] = []
        self.limit = 0
        self.poly = Polygon(
            [
                v2([  0,   0]),
                v2([  0, 200]),
                v2([200, 200]),
                v2([200,   0]),
                # v2([ 0*2, 0*2]),
                # v2([50*2, 0*2]),
                # v2([50*2,60*2]),
                # v2([40*2,70*2]),
                # v2([ 0*2,60*2])
            ],
        )
        self.max_l = 50
        self.active_lines = set()
        self.generate_new_lines()
    

    def generate_new_lines(self):
        self.lines.clear()
        self.active_lines.clear()
        max_l = 50
        t = 1
        for i in range(100):
            x, y = [
                randint(-self.w//2 + t*max_l, self.w // 2 - t*max_l),
                randint(-self.h//2 + t*max_l, self.h // 2 - t*max_l)
            ]
            offset = v2([x, y])
            a = v2([0, 0]) + offset
            b = v3([randint(10, self.max_l), 0, 0]).rotate(0, 0, randint(0, 360)).to_v2() + offset
            self.lines.append(
                Line(a, b)
            )
        self.repaint()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.handle_resize()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(self.mainPen)
        # self.draw_window(painter)
        self.draw_lines(painter)
        self.draw_border(painter)
        self.poly.draw(painter, self.center)
        self.draw_polygon_points(painter)
        self.draw_polygon_current_point(painter)
        self.draw_highlited_lines(painter)
        painter.end()
    
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        for i, point in enumerate(self.poly.points):
            if QtCore.QLineF(point.to_QPoint() + self.center, event.pos()).length() < 20:
                self.mouse_grabbed = True
                self.poly.ci = i
                # print('mouse grabbed:', i)
                break

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_grabbed:
            x, y = event.x(), event.y()
            self.poly.move_point(
                v2([
                    x - self.w//2,
                    y - self.h//2
                ])
            )
            # pass
        # print([x, y])
        self.repaint()
    
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_grabbed = False
        self.map_lines()
        self.repaint()

    def map_lines(self):
        self.active_lines.clear()
        for i, line in enumerate(self.lines):
            # print()
            if i < self.limit:
                if self.poly.contains(line.a, self.center) or self.poly.contains(line.b, self.center):
                    self.active_lines.add(i)
    
    def with_pen(pen: QtGui.QPen):
        def dec(func):
            def wrapper(self, painter: QtGui.QPainter, *args, **kwargs):
                painter.setPen(pen)
                func(self, painter)
                painter.setPen(self.mainPen)
            return wrapper
        return dec

    @with_pen(mainPen)
    def draw_window(self, painter: QtGui.QPainter):
        # for line in self.lines
        painter.drawLine(self.line.to_QLine(self.center))
    
    @with_pen(mainPen)
    def draw_lines(self, painter: QtGui.QPainter):
        # for line in self.lines:
        #     painter.drawLine(line.to_QLine(self.center))
        for i in range(self.limit):
            painter.drawLine(self.lines[i].to_QLine(self.center))
    
    @with_pen(borderPen)
    def draw_border(self, painter: QtGui.QPainter):
        for a, b in zip(self.border[::1], self.border[1::1]):
            painter.drawLine(a,b)
    
    @with_pen(mainPen)
    def draw_polygon_points(self, painter: QtGui.QPainter):
        for point in self.poly.points:
            painter.drawEllipse(
                point.to_QPoint() + self.center,
                5, 5
            )
    
    @with_pen(highlightPen)
    def draw_polygon_current_point(self, painter: QtGui.QPainter):
        ci = self.poly.ci
        painter.drawEllipse(
            self.poly.points[ci].to_QPoint() + self.center,
            5, 5
        )

    @with_pen(highlightPen)
    def draw_highlited_lines(self, painter: QtGui.QPainter):
        for i in self.active_lines:
            if i < self.limit:
                self.lines[i].draw(painter, self.center)


    def handle_resize(self):
        h, w = [self.geometry().height(), self.geometry().width()]
        self.h, self.w = h, w
        self.center = QtCore.QPoint(
            w // 2,
            h // 2
        )
        self.border  = QtGui.QPolygon([
            QtCore.QPoint(0,0),
            QtCore.QPoint(w,0),
            QtCore.QPoint(w,h),
            QtCore.QPoint(0,h),
            QtCore.QPoint(0,0),
        ])
        self.repaint()


class Lab_4(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Lab_4, self).__init__(parent)
        self.ui: ui_lab_4 = ui_lab_4()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        delete(self.ui.moc_drawArea)
        # self.drawArea = DrawArea(self.ui.drawArea)
        # self.ui.drawArea = self.drawArea
        self.drawArea = DrawArea(self)
        self.ui.horizontalLayout_3.addWidget(self.drawArea)
        self.setup_connections()

    def setup_connections(self):
        self.ui.horizontalSlider.valueChanged.connect(
            self.s_handle_slider_change
        )
        self.ui.horizontalSlider_2.valueChanged.connect(
            self.s_handle_slider_2_change
        )
        self.ui.generateLinesButton.clicked.connect(
            lambda: self.drawArea.generate_new_lines()
        )
    
    def s_handle_slider_change(self):
        self.ui.linesCount.setText(str(self.ui.horizontalSlider.value()))
        self.drawArea.limit = self.ui.horizontalSlider.value()
        self.drawArea.repaint()

    def s_handle_slider_2_change(self):
        self.ui.linesLength.setText(f"{self.ui.horizontalSlider_2.value()}px")
        self.drawArea.max_l = self.ui.horizontalSlider_2.value()
