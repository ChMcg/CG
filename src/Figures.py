from __future__ import annotations
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from typing import Dict, Literal, Tuple, List, Union
from numpy.matrixlib.defmatrix import matrix as M
import numpy as np

from PyQt5.QtCore import QPoint
from src.Core import Point, v2

class Figure():
    def __init__(self) -> None:
        pass

    def draw(self, painter: QtGui.QPainter, offset: QtCore.QPoint = QtCore.QPoint(0, 0)):
        raise NotImplementedError()

    def get_points(self) -> List[Point]:
        raise NotImplementedError()

    def move_point(self, pos: v2):
        raise NotImplementedError()

    def get_all_intersections(self, other_line: Line) -> List[Point]:
        raise NotImplementedError()


class LineCounter():
    counter = 0
    
    @staticmethod
    def new_id() -> int:
        LineCounter.counter += 1
        return LineCounter.counter

class Line(Figure):
    def __init__(self, a: Point, b: Point) -> None:
        self.A, self.B = a, b
        self.canonical = Line.make_canonical(a, b)
        self.id = LineCounter.new_id()
    
    def __str__(self) -> str:
        return f"<Line [{self.A}, {self.B}]>"
    
    def __repr__(self) -> str:
        return str(self)
    
    def to_QLine(self, offset: QtCore.QPoint = QtCore.QPoint(0, 0)) -> QtCore.QLine:
        return QtCore.QLine(
            self.A.to_QPoint() + offset,
            self.B.to_QPoint() + offset
        )
    
    def draw(self, painter: QtGui.QPainter, offset: QPoint = QPoint(0, 0)):
        painter.drawLine(self.to_QLine(offset))
        # painter.drawText(
        #     self.A.to_QPoint() + offset,
        #     str(self.A)
        # )
        # painter.drawText(
        #     self.B.to_QPoint() + offset,
        #     str(self.B)
        # )

    def make_canonical(A: v2, B: v2) -> Tuple[int]:
        x_1, y_1 = A.to_list()
        x_2, y_2 = B.to_list()
        a = y_1 - y_2
        b = x_2 - x_1
        c = -x_2*(y_1 - y_2) + y_2*(x_1 - x_2)
        return (a, b, c)

    def contains(self, point: v2, alg: str = 'simple') -> bool:
        if point is None:
            return False
        y_max = max([self.A.y, self.B.y])
        y_min = min([self.A.y, self.B.y])
        x_max = max([self.A.x, self.B.x])
        x_min = min([self.A.x, self.B.x])
        a, b, c = self.canonical
        x, y = point.to_list()
        if alg == 'simple':
            res = a*x + b*y + c
            if a*x + b*y + c < 10**-9:
                if y - y_min + 10**-9 >= 0 and y_max-y + 10**-9 >= 0:
                    if x - x_min + 10**-9 >= 0 and x_max-x + 10**-9 >= 0:
                        return True
        return False

    def intersection(self, line: Line, cache: Dict[Tuple, v2] = None) -> Union[v2, None]:
        id_pair = frozenset({self.id, line.id})
        if cache is not None:
            if id_pair in cache.keys():
                return cache[id_pair]
        a_1, b_1, c_1 = self.canonical
        a_2, b_2, c_2 = line.canonical
        a = M([
                [a_1, b_1],
                [a_2, b_2]
            ])
        b = M([
                [-c_1],
                [-c_2]
            ])
        try:
            x = np.linalg.inv(a) * b
        except np.linalg.LinAlgError:
            return None
        if cache is not None:
            cache[id_pair] = Point.from_matrix(x)
        return Point.from_matrix(x)

class Polygon(Figure):
    def __init__(self, points: List[v2]):
        self.points: List[v2] = points
        self.lines: List[Line] = []
        self.cache: Dict[set, v2] = dict()
        self.regenerate_lines()
        self.qt_poly = QtGui.QPolygon([x.to_QPoint() for x in points])
        self.ci = 0
        self.x_r_max = max([point.x for point in self.points])

    def regenerate_lines(self):
        self.lines.clear()
        self.cache.clear()
        for A,B in zip(self.points[::1], self.points[1::1] + [self.points[0],]):
            self.lines.append(Line(A,B))

    def draw(self, painter: QtGui.QPainter, offset: QtCore.QPoint = QtCore.QPoint(0, 0)):
        for a, b in zip(self.points[::1], self.points[1::1] + [self.points[0],]):
            painter.drawLine(
                a.to_QPoint() + offset,
                b.to_QPoint() + offset
            )
            # painter.drawText(
            #     a.to_QPoint() + offset,
            #     str(a)
            # )
            # painter.drawText(
            #     b.to_QPoint() + offset,
            #     str(b)
            # )
        # for key, point in self.cache:
        #     painter.drawEllipse(
        #         point.to_QPoint() + offset,
        #         2,2
        #     )
    
    def contains(self, point: v2, offset: QPoint):
        temp_line = Line(point, v2([self.x_r_max + 2, point.y]))
        cnt = 0
        for line in self.lines:
            intersection = line.intersection(temp_line, self.cache)
            if line.contains(intersection) and temp_line.contains(intersection):
                cnt += 1
        if cnt % 2 == 0:
            return False
        else:
            return True

    def intersection(self, other_line: Line):
        for line in self.lines:
            intersection = line.intersection(other_line, self.cache)
            if line.contains(intersection) and other_line.contains(intersection):
                return intersection
        return None

    def qt_contains(self, point: v2, offset: QPoint):
        self.qt_poly = QtGui.QPolygon([x.to_QPoint() for x in self.points])
        return self.qt_poly.containsPoint(
            point.to_QPoint(),
            QtCore.Qt.WindingFill
            # QtCore.Qt.OddEvenFill
        )
    
    def move_point(self, pos: v2):
        self.points[self.ci] = pos
        # if self.x_r_max < pos.x:
        #     self.x_r_max = pos.x
        #TODO: хранить индекс самой правой точки
        self.x_r_max = max([point.x for point in self.points])
        self.regenerate_lines()

    def get_points(self) -> List[Point]:
        return self.points

    def get_all_intersections(self, other_line: Line) -> List[Point]:
        ret = []
        for line in self.lines:
            intersection = line.intersection(other_line, self.cache)
            if line.contains(intersection) and other_line.contains(intersection):
                ret.append(intersection)
                # return intersection
        return ret


if __name__ == "__main__":
    a = Line(v2([0,1]),v2([6,4]))
    b = Line(v2([8,8]),v2([8,0]))
    C = a.intersection(b)
    p = v2([0,1])
