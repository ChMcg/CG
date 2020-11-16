from src.Core import v2, v3
from typing import Literal, Tuple, List
from numpy import linspace
from math import factorial


class Bezier:
    default_points = [
        v2(( 10,  10)),
        v2(( 20, 200)),
        v2((500,  10)),
        v2((500, 300))
    ]

    def __init__(self, points: List[v3] = default_points):
        self.points: List[v2] = points
        print(points)
        self.n = len(points) - 1
        self.point = v2((0, 0))
        self.current_point = self.points[0]
        self.current_index = 0
        self.spline_points: List[v2] = []
        self.calculate()

    def calculate(self):
        x = [point.x for point in self.points]
        y = [point.y for point in self.points]
        n = self.n
        self.spline_points.clear()
        for t in linspace(0, 1, 50):
            tmp_x = sum([
                self.N(i, n, t)*x[i]
                for i in range(0,n+1)
            ])
            tmp_y = sum([
                self.N(i, n, t)*y[i]
                for i in range(0,n+1)
            ])
            self.spline_points.append(v2((tmp_x, tmp_y)))

    def N(self, i: int, n: int, t: float):
        res = ( factorial(n) )/( factorial(i)*factorial(n-i) ) \
            * t**(i) * (1-t)**(n-i)
        return res

    def set_current_index(self, index):
        self.current_index = index


if __name__ == "__main__":
    a = Bezier()
