from __future__ import annotations
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from typing import Literal, Tuple, List

from PyQt5.QtCore import QPoint
from src.Core import Point, v2

class Line():
    def __init__(self, a: Point, b: Point) -> None:
        self.a, self.b = a, b
    
    def __str__(self) -> str:
        return f"<Line [{self.a}, {self.b}]>"
    
    def __repr__(self) -> str:
        return str(self)
    
    def to_QLine(self, offset: QtCore.QPoint = QtCore.QPoint(0, 0)) -> QtCore.QLine:
        return QtCore.QLine(
            self.a.to_QPoint() + offset,
            self.b.to_QPoint() + offset
        )
    
    def draw(self, painter: QtGui.QPainter, offset: QPoint = QPoint(0, 0)):
        painter.drawLine(self.to_QLine(offset))



class Polygon():
    def __init__(self, points: List[v2]):
        self.points: List[v2] = points
        self.qt_poly = QtGui.QPolygon([x.to_QPoint() for x in points])
        self.ci = 0
    
    def draw(self, painter: QtGui.QPainter, offset: QtCore.QPoint = QtCore.QPoint(0, 0)):
        for a, b in zip(self.points[::1], self.points[1::1] + [self.points[0],]):
            painter.drawLine(
                a.to_QPoint() + offset,
                b.to_QPoint() + offset
            )
    
    def contains(self, point: v2, offset: QPoint):
        self.qt_poly = QtGui.QPolygon([x.to_QPoint() for x in self.points])
        return self.qt_poly.containsPoint(
            point.to_QPoint(),
            QtCore.Qt.WindingFill
            # QtCore.Qt.OddEvenFill
        )
    
    def move_point(self, pos: v2):
        self.points[self.ci] = pos
