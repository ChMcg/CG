from PyQt5 import QtCore, QtWidgets, QtGui
from sip import delete
from ui.lab_5 import Ui_Form as ui_lab_5
from src.Core import Point, v2, v3
from src.Figures import Figure,  Line, Polygon
from typing import Dict, Literal, Tuple, List
from random import randint
from time import sleep
from copy import copy


class DrawArea(QtWidgets.QWidget):
    mainPen             = QtGui.QPen(QtGui.QColor(0x0d47a1), 1)
    highlightPen        = QtGui.QPen(QtGui.QColor(0xFFA0A0), 3)
    # highlightPen        = QtGui.QPen(QtGui.QColor(0xFF, 0xA0, 0xA0, 0xA0), 3)
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
        self.cf = None
        self.cache: List[List[Line]] = []
        self.colors: List[QtGui.QColor] = []
        self.update_on_mouse_move = False
        self.line_width = 3
        self.line_period = 6
        self.delay = None
        self.handle_resize()

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
        # for figure in self.figures:
        #     figure.draw(painter, self.center)
        #     for point in figure.get_points():
        #         painter.drawEllipse(
        #             point.to_QPoint() + self.center,
        #             5,5
        #         )
        # self.draw_highlited_points(painter)
        self.draw_cache(painter)
        painter.end()

    def update_cache(self):
        self.cache.clear()
        h, w = [self.geometry().height(), self.geometry().width()]
        # lines = [Line(v2([0,y]), v2([w,y])) for y in range(0,h,3)]
        c = self.center
        cache = []
        new_cache= {}

        for y in range(0, h, self.line_period):
            line = Line(
                    v2([
                        0 - c.x(),
                        y - c.y()
                    ]), 
                    v2([
                        w - c.x(),
                        y - c.y()
                    ]), 
                )
            line_cache = []
            cl = -1
            current_color = [QtGui.QColor(0xFF0000),]
            tmp: List[Tuple[Point, str, QtGui.QColor]] = []
            intersection = []
            for i, figure in enumerate(self.figures):
                intersection = figure.get_all_intersections(line)
                if len(intersection) == 2:
                    # intersection.sort(key=lambda point: point.x)
                    A, B = intersection
                    if A.x > B.x:
                        A, B = B, A 
                    tmp.append((A, 'start', i, self.colors[i]))
                    tmp.append((B,  'stop', i, self.colors[i]))
                # print(len(intersection))

            if len(tmp) > 0:
                tmp.sort(key=lambda item: item[0].x)
                for a,b in zip(tmp[::1], tmp[1::1]):
                    a_point, a_state, a_layer, a_color = a 
                    b_point, b_state, b_layer, b_color = b
                    if a_state == 'start':
                        if a_layer > cl:
                            cl = a_layer
                            current_color.append(a_color)
                            line_cache.append(
                                (
                                    Line(
                                        # a_point,
                                        v2([a_point.x + 2, b_point.y]),
                                        b_point
                                        # v2([b_point.x-1, b_point.y])
                                    ), a_color
                                )
                            )
                        else:
                            line_cache.append(
                                (
                                    Line(
                                        # a_point,
                                        v2([a_point.x + 2, b_point.y]),
                                        b_point
                                        # v2([b_point.x-1, b_point.y])
                                    ), current_color[-1]
                                )
                            )
                        if b_state == 'stop':
                            if b_layer == cl:
                                cl = -1
                                current_color.pop()
                    else: # a - stop
                        if a_layer == cl:
                            cl = -1
                            current_color.pop()
                        if b_state == 'start':
                            if cl > -1:
                                line_cache.append(
                                    (
                                        Line(
                                            # a_point,
                                            v2([a_point.x + 2, b_point.y]),
                                            b_point
                                            # v2([b_point.x-1, b_point.y])
                                        ), current_color[-1]
                                    )
                                )

                                pass
                            else: # no layer
                                pass
                            pass
                        else: # b - stop
                            if cl > -1:
                                line_cache.append(
                                    (
                                        Line(
                                            # a_point,
                                            v2([a_point.x + 2, b_point.y]),
                                            b_point
                                            # v2([b_point.x-1, b_point.y])
                                        ), current_color[-1]
                                    )
                                )
                            else: # cl == -1
                                line_cache.append(
                                    (
                                        Line(
                                            # a_point,
                                            v2([a_point.x + 2, b_point.y]),
                                            b_point
                                            # v2([b_point.x-1, b_point.y])
                                        ), b_color
                                    )
                                )

                            pass
                        pass
            cache.append(line_cache)
            new_cache[y] = line_cache
        self.cache = cache

    def add_figure(self, fig: Figure):
        self.figures.append(fig)
        self.colors.append(QtGui.QColor(*[randint(0,255) for x in [1,2,3]], 0x60))
        # self.colors.append(QtGui.QColor(*[randint(0,255) for x in [1,2,3]], 0xFF))
    
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        for k, figure in enumerate(self.figures):
            for i, point in enumerate(figure.get_points()):
                if QtCore.QLineF(point.to_QPoint() + self.center, event.pos()).length() < 20:
                    self.mouse_grabbed = True
                    self.cf = k
                    figure.ci = i
                    break

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_grabbed:
            x, y = event.x(), event.y()
            self.figures[self.cf].move_point(
                v2([
                    x - self.w//2,
                    y - self.h//2
                ])
            )
            if self.update_on_mouse_move:
                self.update_cache()
        self.repaint()
    
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_grabbed = False
        self.update_cache()
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
    
    @with_pen(highlightPen)
    def draw_highlited_points(self, painter: QtGui.QPainter):
        if self.cf is not None:
            figure = self.figures[self.cf]
            painter.drawEllipse(
                figure.get_points()[figure.ci].to_QPoint() + self.center,
                5,5
            )

    @with_pen(mainPen)
    def draw_cache(self, painter: QtGui.QPainter):
        painter.setPen(QtGui.QPen(QtGui.QColor(0x101010), 3))
        for line_cache in self.cache:
            if self.delay is not None:
                # sleep(self.delay*10**(-3))
                sleep(1/1000)
            for item in line_cache:
                line, color = item
                if color is not None:
                    painter.setPen(QtGui.QPen(color, self.line_width))
                line.draw(painter, self.center)
                self.update()


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
        self.ui._cbUseRepaintOnUpdate.click()

    def setup_connections(self):
        self.ui._hsLineWidth.valueChanged.connect(self.s_line_width)
        self.ui._cbUseRepaintOnUpdate.clicked.connect(self.s_use_repaint_on_update)
        self.ui._hsLinePeriod.valueChanged.connect(self.s_line_period)
        self.ui._pbAddFigure.clicked.connect(self.s_add_figure)

    def s_line_width(self):
        lw = self.ui._hsLineWidth.value()
        self.drawArea.line_width = lw
        self.ui._lLineWidth.setText(f"{lw}px")
        self.drawArea.update_cache()
        self.drawArea.repaint()

    def s_use_repaint_on_update(self):
        self.ui._pbRepaint.setEnabled(
                not self.ui._cbUseRepaintOnUpdate.isChecked()
            )
        self.drawArea.update_on_mouse_move = self.ui._cbUseRepaintOnUpdate.isChecked()

    def s_line_period(self):
        lp = self.ui._hsLinePeriod.value()
        self.drawArea.line_period = lp
        self.ui._lLinePeriod.setText(f"{lp}px")
        self.drawArea.update_cache()
        self.drawArea.repaint()

    def init_figures(self):
        self.figures = self.drawArea.generate_figures()
        for index, name in self.figures.keys():
            self.ui._cbFigure.addItem(name)
        # self.drawArea.figures.append(list(self.figures.values())[0])
        # self.drawArea.add_figure(list(self.figures.values())[0])
        # self.drawArea.add_figure(list(self.figures.values())[1])
        self.drawArea.update_cache()
        self.drawArea.repaint()

    def s_add_figure(self):
        ci = self.ui._cbFigure.currentIndex()
        name = self.ui._cbFigure.currentText()
        self.drawArea.add_figure(
            # copy(self.figures[(ci, name)])
            Polygon(copy(self.figures[(ci, name)].points))
        )
        self.drawArea.update_cache()
        self.drawArea.repaint()


