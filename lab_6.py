from PyQt5 import QtCore, QtWidgets, QtGui
import OpenGL.GL as gl
from sip import delete
from ui.lab_6 import Ui_Form as ui_lab_6
from src.Core import Point, v2, v3
from src.Figures import Figure,  Line, Polygon
from typing import Dict, Literal, Tuple, List, Optional
from random import randint
from time import sleep
from copy import copy
import math


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

def mk_color(color: int) -> List[float]:
    return [
                eval(f"0x{x}")/256 
                for x in [
                        hex(color)[2:][0+i:2+i] 
                        for i in range(0,6,2)
                    ]
            ]


class GLDrawArea(QtWidgets.QOpenGLWidget):
    xRotationChanged = QtCore.pyqtSignal(int) 
    yRotationChanged = QtCore.pyqtSignal(int)
    zRotationChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.setMinimumSize(500,500)
        self.setMaximumSize(500,500)
        self.gear1 = 0
        self.gear2 = 0
        self.gear3 = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.gear1Rot = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.advanceGears)

    def setXRotation(self, angle):
        self.normalizeAngle(angle)
        self
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side, side)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glFrustum(-1.0, +1.0, -1.0, 1.0, 5.0, 60.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslated(0.0, 0.0, -40.0)

    def initializeGL(self) -> None:
        lightPos = (5.0, 5.0, 10.0, 1.0)
        reflectance1 = (*mk_color(0xAB47BC), 1.0)
        reflectance2 = (*mk_color(0xD4E157), 1.0)
        reflectance3 = (*mk_color(0xE91E63), 1.0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, lightPos)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        self.gear1 = self.makeGear(reflectance1, 1.0, 4.0, 1.0, 0.7, 20) # 20 10 10
        self.gear2 = self.makeGear(reflectance2, 0.5, 2.0, 2.0, 0.7, 10)
        self.gear3 = self.makeGear(reflectance3, 1.3, 2.0, 0.5, 0.7, 10)
        gl.glEnable(gl.GL_NORMALIZE)
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    
    def makeGear(self, reflectance, innerRadius, outerRadius, thickness, toothSize, toothCount):
        list = gl.glGenLists(1)
        gl.glNewList(list, gl.GL_COMPILE)
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE,
                reflectance)

        r0 = innerRadius
        r1 = outerRadius - toothSize / 2.0
        r2 = outerRadius + toothSize / 2.0
        delta = (2.0 * math.pi / toothCount) / 4.0
        z = thickness / 2.0

        gl.glShadeModel(gl.GL_FLAT)

        for i in range(2):
            if i == 0:
                sign = +1.0
            else:
                sign = -1.0

            gl.glNormal3d(0.0, 0.0, sign)

            gl.glBegin(gl.GL_QUAD_STRIP)

            for j in range(toothCount+1):
                angle = 2.0 * math.pi * j / toothCount
                gl.glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), sign * z)
                gl.glVertex3d(r1 * math.cos(angle), r1 * math.sin(angle), sign * z)
                gl.glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), sign * z)
                gl.glVertex3d(r1 * math.cos(angle + 3 * delta), r1 * math.sin(angle + 3 * delta), sign * z)

            gl.glEnd()

            gl.glBegin(gl.GL_QUADS)

            for j in range(toothCount):
                angle = 2.0 * math.pi * j / toothCount
                gl.glVertex3d(r1 * math.cos(angle), r1 * math.sin(angle), sign * z)
                gl.glVertex3d(r2 * math.cos(angle + delta), r2 * math.sin(angle + delta), sign * z)
                gl.glVertex3d(r2 * math.cos(angle + 2 * delta), r2 * math.sin(angle + 2 * delta), sign * z)
                gl.glVertex3d(r1 * math.cos(angle + 3 * delta), r1 * math.sin(angle + 3 * delta), sign * z)

            gl.glEnd()

        gl.glBegin(gl.GL_QUAD_STRIP)

        for i in range(toothCount):
            for j in range(2):
                angle = 2.0 * math.pi * (i + (j / 2.0)) / toothCount
                s1 = r1
                s2 = r2

                if j == 1:
                    s1, s2 = s2, s1

                gl.glNormal3d(math.cos(angle), math.sin(angle), 0.0)
                gl.glVertex3d(s1 * math.cos(angle), s1 * math.sin(angle), +z)
                gl.glVertex3d(s1 * math.cos(angle), s1 * math.sin(angle), -z)

                gl.glNormal3d(s2 * math.sin(angle + delta) - s1 * math.sin(angle), s1 * math.cos(angle) - s2 * math.cos(angle + delta), 0.0)
                gl.glVertex3d(s2 * math.cos(angle + delta), s2 * math.sin(angle + delta), +z)
                gl.glVertex3d(s2 * math.cos(angle + delta), s2 * math.sin(angle + delta), -z)

        gl.glVertex3d(r1, 0.0, +z)
        gl.glVertex3d(r1, 0.0, -z)
        gl.glEnd()

        gl.glShadeModel(gl.GL_SMOOTH)

        gl.glBegin(gl.GL_QUAD_STRIP)

        for i in range(toothCount+1):
            angle = i * 2.0 * math.pi / toothCount
            gl.glNormal3d(-math.cos(angle), -math.sin(angle), 0.0)
            gl.glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), +z)
            gl.glVertex3d(r0 * math.cos(angle), r0 * math.sin(angle), -z)

        gl.glEnd()

        gl.glEndList()

        return list

    def paintGL(self) -> None:
        gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glPushMatrix()
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)

        self.drawGear(self.gear1, -3.0, -2.0, 0.0, self.gear1Rot / 16.0)
        self.drawGear(self.gear2, +3.1, -2.0, 0.0,
                -2.0 * (self.gear1Rot / 16.0) - 9.0)

        gl.glRotated(+90.0, 1.0, 0.0, 0.0)
        self.drawGear(self.gear3, -3.1, -1.8, -2.2,
                +2.0 * (self.gear1Rot / 16.0) - 2.0)

        gl.glPopMatrix()

    def drawGear(self, gear, dx, dy, dz, angle):
        gl.glPushMatrix()
        gl.glTranslated(dx, dy, dz)
        gl.glRotated(angle, 0.0, 0.0, 1.0)
        gl.glCallList(gear)
        gl.glPopMatrix()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def advanceGears(self):
        self.gear1Rot += 2 * 16
        self.update()

    def xRotation(self):
        return self.xRot

    def yRotation(self):
        return self.yRot

    def zRotation(self):
        return self.zRot

    def normalizeAngle(self, angle):
        while (angle < 0):
            angle += 360 * 16

        while (angle > 360 * 16):
            angle -= 360 * 16
    
    def start(self):
        self.timer.start(30)
    
    def stop(self):
        self.timer.stop()



class Lab_6(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Lab_6, self).__init__(parent)
        self.ui: ui_lab_6 = ui_lab_6()
        self.ui.setupUi(self)
        self.setMouseTracking(True)
        self.drawArea = GLDrawArea(self)
        delete(self.ui.moc_drawArea)
        self.ui.horizontalLayout.addWidget(self.drawArea)
        self.gear_running = False
        self.setup_connections()

    def setup_connections(self):
        self.ui.pause.clicked.connect(self.handle_pause)

    def handle_pause(self):
        if self.gear_running:
            self.drawArea.stop()
            self.ui.pause.setText('Запуск')
            self.gear_running = False
        else:
            self.drawArea.start()
            self.ui.pause.setText('Пауза')
            self.gear_running = True

