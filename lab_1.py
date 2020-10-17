from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import qDebug
from ui.lab_1 import Ui_Form as ui_lab_1
from src.Drawable import Cube, Axes


class DrawArea(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainPen = QtGui.QPen(QtGui.QColor(0x0d47a1), 3)
        self.setGeometry(parent.geometry())
        self.a = QtCore.QPoint(
            self.geometry().height() // 2,
            self.geometry().width() // 2
        )
        x, y = self.a.x(), self.a.y()
        self.cube = Cube(200, (x, y, 0))

    def paintEvent(self, event: QtGui.QPaintEvent):
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.setPen(self.mainPen)
        self.cube.draw(self.painter)
        self.painter.end()


class Lab_1(QtWidgets.QWidget):
    def __init__(self, some):
        super(Lab_1, self).__init__(some)
        self.ui: ui_lab_1 = ui_lab_1()
        self.ui.setupUi(self)
        self.drawArea = DrawArea(self.ui.drawArea)
        self.ui.drawArea = self.drawArea
        self.ui.setSide.setValue(200)
        self.ui.setSide.valueChanged.connect(self.s_cube_size)
        self.ui.rotateX.valueChanged.connect(self.s_cube_rotation)
        self.ui.rotateY.valueChanged.connect(self.s_cube_rotation)
        self.ui.rotateZ.valueChanged.connect(self.s_cube_rotation)

    def setupUi(self, target: QtWidgets.QWidget):
        self.ui.setupUi(target)
        self.update()

    def s_cube_size(self):
        c = self.drawArea.cube.center
        cr = self.drawArea.cube.current_rotation
        self.drawArea.cube = Cube(self.ui.setSide.value(), c)
        self.drawArea.cube.rotate_to(*cr)
        self.drawArea.repaint()

    def s_cube_rotation(self):
        self.drawArea.cube.rotate_to(
            self.ui.rotateX.value(),
            self.ui.rotateY.value(),
            self.ui.rotateZ.value()
        )
        self.drawArea.repaint()
