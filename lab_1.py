from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from ui.lab_1 import Ui_Form as ui_lab_1
from src.Drawable import Cube, Axis, AxisType


class DrawArea(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.mainPen = QtGui.QPen(QtGui.QColor(0x0d47a1), 3)
        self.axisPen = QtGui.QPen(QtGui.QColor(0x000000), 3)
        self.polygonsPen = QtGui.QPen(QtGui.QColor(0x000000), 3)
        self.polygonsBrush = QtGui.QBrush(QtGui.QColor(0x0d47a1))
        self.setGeometry(parent.geometry())
        self.a = QtCore.QPoint(
            self.geometry().height() // 2,
            self.geometry().width() // 2
        )
        x, y = self.a.x(), self.a.y()
        self.c = (x, y, 0)
        self.cube = Cube(200, (x, y, 0))
        self.axis = [
            Axis(250, (x,y), AxisType.X),
            Axis(250, (x,y), AxisType.Y),
            Axis(250, (x,y), AxisType.Z)
        ]

    def paintEvent(self, event: QtGui.QPaintEvent):
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.setPen(self.mainPen)
        self.cube.draw(self.painter)
        # self.painter.setPen(self.polygonsPen)
        # self.painter.setBrush(self.polygonsBrush)
        # self.cube.draw_polygons(self.painter)
        # # self.painter.setBrush()
        self.painter.setPen(self.axisPen)
        for axis in self.axis:
            axis.draw(self.painter)
        self.painter.end()


class Lab_1(QtWidgets.QWidget):
    def __init__(self, some):
        super(Lab_1, self).__init__(some)
        self.ui: ui_lab_1 = ui_lab_1()
        self.ui.setupUi(self)
        self.drawArea = DrawArea(self.ui.drawArea)
        self.ui.drawArea = self.drawArea
        self.ui.setSide.setValue(200)
        self.setup_connections()
        self.s_reset_axes()
        
    def setup_connections(self):
        self.ui.setSide.valueChanged.connect(self.s_cube_size)
        self.ui.rotateX.valueChanged.connect(self.s_cube_rotation)
        self.ui.rotateY.valueChanged.connect(self.s_cube_rotation)
        self.ui.rotateZ.valueChanged.connect(self.s_cube_rotation)
        self.ui.rotateX.valueChanged.connect(lambda: self.ui.labelX.setText(str(self.ui.rotateX.value())))
        self.ui.rotateY.valueChanged.connect(lambda: self.ui.labelY.setText(str(self.ui.rotateY.value())))
        self.ui.rotateZ.valueChanged.connect(lambda: self.ui.labelZ.setText(str(self.ui.rotateZ.value())))
        self.ui.rotateAxisX.valueChanged.connect(self.s_axis_rotation)
        self.ui.rotateAxisY.valueChanged.connect(self.s_axis_rotation)
        self.ui.rotateAxisZ.valueChanged.connect(self.s_axis_rotation)
        self.ui.rotateAxisX.valueChanged.connect(lambda: self.ui.labelAxisX.setText(str(self.ui.rotateAxisX.value())))
        self.ui.rotateAxisY.valueChanged.connect(lambda: self.ui.labelAxisY.setText(str(self.ui.rotateAxisY.value())))
        self.ui.rotateAxisZ.valueChanged.connect(lambda: self.ui.labelAxisZ.setText(str(self.ui.rotateAxisZ.value())))
        self.ui.resetButton.clicked.connect(self.s_reset_axes)

    def setupUi(self, target: QtWidgets.QWidget):
        self.ui.setupUi(target)
        self.update()

    def s_cube_size(self):
        # cr = self.drawArea.cube.current_rotation
        self.drawArea.cube = Cube(self.ui.setSide.value(), self.drawArea.c)
        # self.drawArea.cube.rotate_to(*cr)
        self.s_cube_rotation()
        self.drawArea.repaint()

    def s_cube_rotation(self):
        self.drawArea.cube = Cube(self.ui.setSide.value(), self.drawArea.c)
        self.drawArea.cube.rotate_to(
            self.ui.rotateX.value(),
            self.ui.rotateY.value(),
            self.ui.rotateZ.value()
        )
        self.drawArea.cube.rotate(
            self.ui.rotateAxisX.value(),
            self.ui.rotateAxisY.value(),
            self.ui.rotateAxisZ.value()
        )
        self.drawArea.repaint()

    def s_axis_rotation(self):
        self.drawArea.axis = [
            Axis(250, self.drawArea.c[0:2], AxisType.X),
            Axis(250, self.drawArea.c[0:2], AxisType.Y),
            Axis(250, self.drawArea.c[0:2], AxisType.Z)
        ]
        for axis in self.drawArea.axis:
            axis.rotate(
                self.ui.rotateAxisX.value(),
                self.ui.rotateAxisY.value(),
                self.ui.rotateAxisZ.value()
            )
        self.drawArea.cube = Cube(self.ui.setSide.value(), self.drawArea.c)
        self.drawArea.cube.rotate_to(
            self.ui.rotateX.value(),
            self.ui.rotateY.value(),
            self.ui.rotateZ.value()
        )
        self.drawArea.cube.rotate(
            self.ui.rotateAxisX.value(),
            self.ui.rotateAxisY.value(),
            self.ui.rotateAxisZ.value()
        )
        self.drawArea.repaint()

    def s_reset_axes(self):
        self.ui.rotateAxisX.setValue(-77)
        self.ui.rotateAxisY.setValue( 15)
        self.ui.rotateAxisZ.setValue( -3)
