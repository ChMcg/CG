from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from typing import Tuple, List
import numpy as np
from numpy.matrixlib import matrix
from itertools import chain
from math import sin, cos, radians


class v2:
    def __init__(self, vec: Tuple[int, int]):
        self.m = point_2d(*vec)

    def to_QPoint(self) -> QtCore.QPoint:
        x, y = list(chain(*self.m.tolist()))
        return QtCore.QPoint(x, y)


class v3:
    def __init__(self, vec: Tuple[int, int, int]):
        self.m = point_3d(*vec)

    def __str__(self) -> str:
        tmp = ','.join([str(x) for x in list(chain(*self.m.tolist()))])
        return f"({tmp})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_v2(self) -> v2:
        return v2(tuple(chain(*self.m[0:2].tolist())))

    def __add__(self, vec: Tuple[int, int, int]):
        m: matrix = self.m + point_3d(*vec)
        return v3(tuple(chain(*m.tolist())))

    def __mul__(self, sec: matrix):
        m: matrix = self.m * sec
        # assert m.count() == 3
        # return v3(tuple(chain(*m.tolist())))
        return m

    def x_rotate(self, angle: int):
        a = radians(angle)
        tmp = matrix([
            [1,      0,       0],
            [0, cos(a), -sin(a)],
            [0, sin(a),  cos(a)]
        ])
        self.m = tmp * self.m

    def y_rotate(self, angle: int):
        a = radians(angle)
        tmp = matrix([
            [ cos(a), 0, sin(a)],
            [      0, 1,      0],
            [-sin(a), 0, cos(a)]
        ])
        self.m = tmp * self.m

    def z_rotate(self, angle: int):
        a = radians(angle)
        tmp = matrix([
            [cos(a), -sin(a), 0],
            [sin(a),  cos(a), 0],
            [     0,       0, 1]
        ])
        self.m = tmp * self.m

    def rotate(self, rX: int, rY: int, rZ: int):
        self.x_rotate(rX)
        self.y_rotate(rY)
        self.z_rotate(rZ)


def point_3d(x: int, y: int, z: int) -> matrix:
    return np.matrix(
        [
            [x],
            [y],
            [z]
        ]
    )


def point_2d(x: int, y: int) -> matrix:
    return np.matrix(
        [
            [x],
            [y]
        ]
    )


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
            A = (self.points[a-1] + self.center).to_v2().to_QPoint()
            B = (self.points[b-1] + self.center).to_v2().to_QPoint()
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
