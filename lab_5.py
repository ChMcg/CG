from PyQt5 import QtCore, QtWidgets, QtGui
from sip import delete
from ui.lab_5 import Ui_Form as ui_lab_5
from src.Core import Point, v2, v3
from src.Figures import Figure,  Line, Polygon
from typing import Dict, Literal, Tuple, List
from random import randint


class DrawArea(QtWidgets.QWidget):
    mainPen             = QtGui.QPen(QtGui.QColor(0x0d47a1), 1)
    highlightPen        = QtGui.QPen(QtGui.QColor(0xFFA0A0), 3)
    borderPen           = QtGui.QPen(QtGui.QColor(0xA0A0A0), 4)
    tempHighlightPen    = QtGui.QPen(QtGui.QColor(0xFF0000), 1)

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.mouse_grabbed = False
        self.setGeometry(parent.geometry())
        self.setMinimumSize(550, 550)
        parent.resize(parent.minimumSize())
        self.figures: List[Figure] = []

    def generate_figures(self) ->  Dict[Tuple[int, str], Figure]:
        ret = {}
        ret[(0, 'Треугольник')] = Polygon([
            v2([  0,  0]),
            v2([100,  0]),
            v2([  0,200]),
        ])
        ret[(1, 'Четырёхугольник')] = Polygon([
            v2([  0,  0]),
            v2([100,  0]),
            v2([100,200]),
            v2([  0,200]),
        ])
        return ret

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.handle_resize()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(self.mainPen)
        self.draw_border(painter)
        for figure in self.figures:
            figure.draw(painter, self.center)
        painter.end()
    
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        pass
        # for i, point in enumerate(self.poly.points):
        #     if QtCore.QLineF(point.to_QPoint() + self.center, event.pos()).length() < 20:
        #         self.mouse_grabbed = True
        #         self.poly.ci = i
        #         break

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_grabbed:
            x, y = event.x(), event.y()
            # self.poly.move_point(
            #     v2([
            #         x - self.w//2,
            #         y - self.h//2
            #     ])
            # )
        self.repaint()
    
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_grabbed = False
        self.repaint()

    def with_pen(pen: QtGui.QPen):
        def dec(func):
            def wrapper(self, painter: QtGui.QPainter, *args, **kwargs):
                painter.setPen(pen)
                func(self, painter)
                painter.setPen(self.mainPen)
            return wrapper
        return dec
    
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

    @with_pen(borderPen)
    def draw_border(self, painter: QtGui.QPainter):
        for a, b in zip(self.border[::1], self.border[1::1]):
            painter.drawLine(a,b)


class Lab_5(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Lab_5, self).__init__(parent)
        self.ui: ui_lab_5 = ui_lab_5()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        delete(self.ui.moc_drawArea)
        # self.drawArea = DrawArea(self.ui.drawArea)
        # self.ui.drawArea = self.drawArea
        self.drawArea = DrawArea(self)
        self.ui.horizontalLayout_4.addWidget(self.drawArea)
        self.figures: Dict[Tuple[int, str], Figure] = {}
        self.setup_connections()
        self.init_figures()

    def setup_connections(self):
        self.ui._hsLineWidth.valueChanged.connect(self.s_line_width)
        self.ui._hsDelay.valueChanged.connect(self.s_delay_time)
        self.ui._cbUseDelay.clicked.connect(self.s_use_delay)
        self.ui._cbUseRepaintOnUpdate.clicked.connect(
            lambda: self.ui._pbRepaint.setEnabled(
                not self.ui._cbUseRepaintOnUpdate.isChecked()
            )
        )

    def s_line_width(self):
        lw = self.ui._hsLineWidth.value()
        self.ui._lLineWidth.setText(f"{lw}px")

    def s_delay_time(self):
        delay = self.ui._hsDelay.value()
        self.ui._lDelayValue.setText(f"{delay}ms")

    def s_use_delay(self):
        checked  = self.ui._cbUseDelay.isChecked()
        self.ui._hsDelay.setEnabled(checked)
        self.ui._lDelayValue.setEnabled(checked)

    def init_figures(self):
        self.figures = self.drawArea.generate_figures()
        for index, name in self.figures.keys():
            self.ui._cbFigure.addItem(name)
        self.drawArea.figures.append(list(self.figures.values())[0])


