from __future__ import annotations
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from typing import Literal, Tuple, List
from itertools import chain
import numpy as np
from numpy.matrixlib import matrix
from math import sin, cos, radians


class Point():
    def __init__(self, dim: int) -> None:
        self.dim = dim
        pass

    def to_QPoint(self) -> QtCore.QPoint:
        raise NotImplementedError()

    def to_list(self) -> List[int]:
        raise NotImplementedError()

    def from_matrix(m: matrix):
        a, b = m.shape
        # assert m.shape == (3,1)
        assert b == 1
        if a == 2:
            return v2(tuple(chain(*m.tolist())))
        elif a == 3:
            return v3(tuple(chain(*m.tolist())))
        else:
            raise NotImplementedError()


class v2(Point):
    def __init__(self, vec: Tuple[int, int]):
        super().__init__(2)
        self.m = point_2d(*vec)
        self.x, self.y = vec

    def __str__(self) -> str:
        tmp = ','.join([f"{x:.2f}" for x in list(chain(*self.m.tolist()))])
        return f"({tmp})"
    
    def __repr__(self) -> str:
        return str(self)

    def __add__(self, other: v2) -> v2:
        m: matrix = self.m + other.m
        return v2(tuple(chain(*m.tolist())))

    def to_QPoint(self) -> QtCore.QPoint:
        x, y = list(chain(*self.m.tolist()))
        return QtCore.QPoint(x, y)

    def to_list(self) -> List[int]:
        return list(chain(*self.m.tolist()))

    def __list__(self) -> List[int]:
        return self.to_list()


class v3(Point):
    def __init__(self, vec: Tuple[int, int, int]):
        super().__init__(3)
        self.m = point_3d(*vec)

    def __str__(self) -> str:
        tmp = ','.join([str(x) for x in list(chain(*self.m.tolist()))])
        return f"({tmp})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_v2(self) -> v2:
        return v2(tuple(chain(*self.m[0:2].tolist())))

    def __add__(self, other: v3) -> v3:
        m: matrix = self.m + other.m
        return v3(tuple(chain(*m.tolist())))

    def __mul__(self, sec: matrix):
        m: matrix = self.m * sec
        return m

    def __rmul__(self, sec: matrix):
        if isinstance(sec, int) or isinstance(sec, float):
            m = sec*self.m
            return v3(tuple(chain(*m.tolist())))
        else:
            raise NotImplementedError()

    def __truediv__(self, other: int) -> v3:
        m: matrix = self.m * (1 / other)
        return v3(tuple(chain(*m.tolist())))

    def __list__(self) -> List:
        return list(chain(*self.m.tolist()))

    def x_rotate(self, angle: int):
        a = radians(angle)
        tmp = matrix([
            [1,      0,       0],
            [0, cos(a), -sin(a)],
            [0, sin(a),  cos(a)]
        ])
        tmp = np.linalg.inv(tmp)
        self.m = tmp * self.m

    def y_rotate(self, angle: int):
        a = radians(angle)
        tmp = matrix([
            [ cos(a), 0, sin(a)],
            [      0, 1,      0],
            [-sin(a), 0, cos(a)]
        ])
        tmp = np.linalg.inv(tmp)
        self.m = tmp * self.m

    def z_rotate(self, angle: int):
        a = radians(angle)
        tmp = matrix([
            [cos(a), -sin(a), 0],
            [sin(a),  cos(a), 0],
            [     0,       0, 1]
        ])
        tmp = np.linalg.inv(tmp)
        self.m = tmp * self.m

    def rotate(self, rX: int, rY: int, rZ: int):
        self.x_rotate(rX)
        self.y_rotate(rY)
        self.z_rotate(rZ)
        return self

    def from_matrix(m: matrix):
        assert m.shape == (3,1)
        return v3(tuple(chain(*m.tolist())))


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
