from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtCore import QPoint
from typing import Literal, Tuple, List
from src.Core import v2, v3
from enum import Enum


class Cube:
    def __init__(self, side: int = 20, center: Tuple[int, int, int] = (0, 0, 0)):
        self.center = center
        self.points = self.generate(side, center)
        self.conn = self.gen_connection()
        self.lines = self.gen_lines()
        self.current_rotation = [0, 0, 0]

    def __repr__(self) -> str:
        return f'[Cube <{id(self)}>] {self.points}'

    def __str__(self) -> str:
        return self.__repr__()

    def draw(self, painter: QtGui.QPainter):
        for line in self.lines:
            painter.drawLine(line)

    def generate(self, side: int, center: Tuple[int, int, int]) -> List[v3]:
        hs = side // 2
        ret = [
            v3((-hs,  hs, -hs)),
            v3((-hs,  hs,  hs)),
            v3(( hs,  hs,  hs)),
            v3(( hs,  hs, -hs)),
            v3((-hs, -hs, -hs)),
            v3((-hs, -hs,  hs)),
            v3(( hs, -hs,  hs)),
            v3(( hs, -hs, -hs))
        ]
        return ret

    def gen_connection(self):
        left = {
            (1, 5), (2, 6), (1, 2), (5, 6)
        }
        bottom = {
            (1, 4), (5, 8), (1, 5), (4, 8)
        }
        right = {
            (3, 4), (7, 8), (3, 7), (4, 8)
        }
        top = {
            (2, 3), (6, 7), (2, 6), (3, 7)
        }
        return {*left, *bottom, *right, *top}

    def gen_lines(self) -> List[QtCore.QLine]:
        ret = []
        for connection in self.conn:
            a, b = connection
            A = (self.points[a-1] + v3(self.center)).to_v2().to_QPoint()
            B = (self.points[b-1] + v3(self.center)).to_v2().to_QPoint()
            ret.append(QtCore.QLine(A, B))
        return ret

    def rotate_to(self, rX: int, rY: int, rZ: int):
        for point in self.points:
            point.rotate(
                rX - self.current_rotation[0],
                rY - self.current_rotation[1],
                rZ - self.current_rotation[2]
            )
        for i, r in enumerate([rX, rY, rZ]):
            self.current_rotation[i] = r
        self.lines = self.gen_lines()
